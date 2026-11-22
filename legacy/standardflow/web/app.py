import base64
import io
import json
from pathlib import Path
import tempfile
import zipfile

from flask import Flask, abort, render_template, request, send_file
from jsonschema.exceptions import ValidationError
from werkzeug.exceptions import BadRequest

from src.checklist import Checklist
from src.main import generate_artifact, validate_data

app = Flask(__name__)
OUTPUT_FORMATS = {
    "png": ("diagram.png", "image/png"),
    "svg": ("diagram.svg", "image/svg+xml"),
    "pdf": ("diagram.pdf", "application/pdf"),
}


@app.errorhandler(ValueError)
@app.errorhandler(ValidationError)
def invalid_data(error):
    message = error.message if isinstance(error, ValidationError) else str(error)
    return BadRequest(description=message)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')

    try:
        output_filename, mimetype = OUTPUT_FORMATS[request.form.get('output_format', 'png')]
    except KeyError:
        abort(400, description='Choose PNG, SVG, or PDF.')
    if 'json_toggle' in request.form:
        data = json.loads(request.form['json_data'])
    else:
        controls = {'diagram_type', 'output_format', 'json_data', 'json_toggle'}
        data = {
            'diagram_type': request.form['diagram_type'],
            **{key: int(value) for key, value in request.form.items() if key not in controls},
        }
    if not isinstance(data, dict) or 'diagram_type' not in data or 'checklist_type' in data:
        abort(400, description='Provide a diagram JSON object.')

    # Request-local files and native downloads avoid shared output state.
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / output_filename
        generate_artifact(data, output)
        encoded = base64.b64encode(output.read_bytes()).decode('ascii')
    return render_template(
        'diagram_viewer.html',
        diagram_file=output.name,
        diagram_url=f'data:{mimetype};base64,{encoded}',
        preview=output_filename.endswith(('.png', '.svg')),
    )


def checklist_data():
    if 'json_toggle' in request.form:
        data = json.loads(request.form['json_data'])
    else:
        checklist_type = request.form['checklist_type']
        indices = sorted(
            (key[3:] for key in request.form if key.startswith('id-') and key[3:].isdigit()),
            key=int,
        )
        items = []
        for index in indices:
            item = {
                field: request.form[f'{field}-{index}']
                for field in ('id', 'section', 'description', 'type')
            }
            if item['type'] == 'multiple_choice':
                prefix = f'option-{index}-'
                options = sorted(
                    (key for key in request.form if key.startswith(prefix) and key[len(prefix):].isdigit()),
                    key=lambda key: int(key[len(prefix):]),
                )
                item['options'] = [request.form[key] for key in options]
            items.append(item)
        data = {
            'checklist_type': checklist_type,
            'title': request.form.get('title', f'{checklist_type} checklist'),
            'items': items,
        }
    if not isinstance(data, dict) or 'checklist_type' not in data or 'diagram_type' in data:
        abort(400, description='Provide a checklist JSON object.')
    return validate_data(data)


@app.route('/checklist', methods=['GET', 'POST'])
def checklist():
    if request.method == 'GET':
        return render_template('checklist.html')
    data = checklist_data()
    return render_template(
        'checklist_viewer.html', data=data,
        sections=Checklist(data).to_markdown_by_section(),
    )


@app.post('/download_checklist')
def download_checklist():
    sections = Checklist(checklist_data()).to_markdown_by_section()
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for section, markdown in sections.items():
            archive.writestr(f"{section.replace(' ', '_')}.md", markdown)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='checklist.zip', mimetype='application/zip')


if __name__ == '__main__':
    app.run()
