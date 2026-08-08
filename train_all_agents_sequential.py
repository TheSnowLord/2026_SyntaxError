import os
import sys
import subprocess

scripts = [
    ('Planner Agent', 'train_planner_agent.py', './fine_tuned_planner'),
    ('Decomposer Agent', 'train_decomposer_agent.py', './fine_tuned_decomposer'),
    ('Researcher Agent', 'train_research_agent.py', './fine_tuned_researcher'),
    ('Developer Agent', 'train_developer_agent.py', './fine_tuned_developer'),
    ('Evaluator Agent', 'train_evaluator_agent.py', './fine_tuned_evaluator'),
]

python_bin = sys.executable

print('=====================================================')
print('  AgentForge AI: Master 5-Agent Local Fine-Tuning')
print('=====================================================\n')

for name, script, outdir in scripts:
    print(f'===> Fine-tuning {name} ({script})...')
    res = subprocess.run([python_bin, script], capture_output=True, text=True)
    if res.returncode == 0:
        print(f'[SUCCESS] {name} trained cleanly -> {outdir}')
    else:
        print(f'[NOTICE] {name} output:')
        print(res.stdout[-300:])
        if res.stderr:
            print(res.stderr[-300:])

print('\n=====================================================')
print('  Fine-Tuned Models Directory Verification Report')
print('=====================================================')

for name, script, outdir in scripts:
    exists = os.path.exists(outdir)
    status_str = 'EXISTS & READY' if exists else 'NOT CREATED YET'
    print(f' - {name:20s}: {outdir:25s} [{status_str}]')
