-- Pandoc Lua filter: convert Markdown task lists and spans into PDF form fields.
-- - Task list items (- [ ] Foo) -> \mkCheckBox[name=...]{ } Foo
-- - Spans with class .textfield -> \mkTextField[name=...,width=...]{label}

local used = {}

local function escape_latex(s)
  local t = {
    ['\\'] = '\\textbackslash{}',
    ['{'] = '\\{',
    ['}'] = '\\}',
    ['_'] = '\\_',
    ['%'] = '\\%',
    ['$'] = '\\$',
    ['#'] = '\\#',
    ['&'] = '\\&',
    ['^'] = '\\^{}',
    ['~'] = '\\textasciitilde{}',
  }
  return (s:gsub('[\\{}_%$#&%^~]', t))
end

local function slugify(s)
  s = s:lower()
  s = s:gsub('[^a-z0-9]+', '-')
  s = s:gsub('^-+', ''):gsub('-+$', '')
  if s == '' then s = 'field' end
  if used[s] then
    used[s] = used[s] + 1
    s = s .. '-' .. tostring(used[s])
  else
    used[s] = 1
  end
  return s
end

function BulletList(list)
  for i, item in ipairs(list) do
    local first = item[1]
    if first and first.t == 'Para' then
      local s = pandoc.utils.stringify(first)
      local mark, label = s:match('^%[([ xX])%]%s*(.+)')
      if mark and label then
        local checked = (mark == 'x' or mark == 'X')
        local name = slugify(label)
        local opt = 'name=' .. name
        if checked then opt = opt .. ',checked=true' end
        local latex = '\\mkCheckBox[' .. opt .. ']{} ' .. escape_latex(label)
        item = { pandoc.Para({ pandoc.RawInline('latex', latex) }) }
        list[i] = item
      end
    end
  end
  return list
end

function Span(el)
  if el.classes:includes('textfield') then
    local label = pandoc.utils.stringify(el)
    local name = el.attributes.name or slugify(label)
    local width = el.attributes.width or '12cm'
    local opts = 'name=' .. name .. ',width=' .. width
    local latex = '\\mkTextField[' .. opts .. ']{' .. escape_latex(label) .. '}'
    return pandoc.RawInline('latex', latex)
  end
  return nil
end

