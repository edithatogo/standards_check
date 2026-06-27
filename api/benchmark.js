const fs = require('fs').promises;
const path = require('path');
const os = require('os');

const ITERATIONS = 1000;

async function setupMockDir() {
    const mockDir = await fs.mkdtemp(path.join(os.tmpdir(), 'benchmark-'));
    for (let i = 0; i < 10000; i++) {
        await fs.writeFile(path.join(mockDir, `file${i}.md`), 'content');
    }
    await fs.writeFile(path.join(mockDir, `targetChecklist.md`), 'target content');
    return mockDir;
}

async function teardownMockDir(mockDir) {
    await fs.rm(mockDir, { recursive: true, force: true });
}

async function oldFindChecklist(dir, checklistId) {
    const files = await fs.readdir(dir);
    const foundFile = files.find(file => path.basename(file, '.md') === checklistId);
    if (foundFile) {
        return path.join(dir, foundFile);
    }
    return null;
}

async function newFindChecklist(dir, checklistId) {
    const targetFile = `${checklistId}.md`;
    const targetPath = path.join(dir, targetFile);
    try {
        await fs.access(targetPath);
        return targetPath;
    } catch (err) {
        return null;
    }
}

async function runBenchmark() {
    console.log('Setting up mock directory with 10,000 files...');
    const mockDir = await setupMockDir();
    const checklistId = 'targetChecklist';

    // Warmup
    await oldFindChecklist(mockDir, checklistId);
    await newFindChecklist(mockDir, checklistId);

    console.log(`Running benchmark with ${ITERATIONS} iterations...`);

    const startOld = process.hrtime.bigint();
    for (let i = 0; i < ITERATIONS; i++) {
        await oldFindChecklist(mockDir, checklistId);
    }
    const endOld = process.hrtime.bigint();
    const timeOld = Number(endOld - startOld) / 1e6; // Convert to ms

    const startNew = process.hrtime.bigint();
    for (let i = 0; i < ITERATIONS; i++) {
        await newFindChecklist(mockDir, checklistId);
    }
    const endNew = process.hrtime.bigint();
    const timeNew = Number(endNew - startNew) / 1e6; // Convert to ms

    console.log(`Old approach (fs.readdir): ${timeOld.toFixed(2)} ms`);
    console.log(`New approach (fs.access): ${timeNew.toFixed(2)} ms`);
    console.log(`Improvement: ${(timeOld / timeNew).toFixed(2)}x faster`);

    console.log('Tearing down mock directory...');
    await teardownMockDir(mockDir);
}

runBenchmark().catch(console.error);
