import pathlib

sections = {}
current = None
buffer = []
with open('synthetic_dataset.txt', 'r', encoding='utf-16-le') as fh:
    for raw_line in fh:
        line = raw_line.strip()
        if line.startswith('\ufeff'):
            line = line.lstrip('\ufeff')
        if not line:
            continue
        if line.startswith('=== ') and line.endswith(' ==='):
            if current is not None:
                sections[current] = '\n'.join(buffer)
            current = line[4:-4]
            buffer = []
        else:
            buffer.append(line)
    if current is not None:
        sections[current] = '\n'.join(buffer)

for name, content in sections.items():
    pathlib.Path(name).write_text(content + '\n', encoding='utf-8')
print("Sections created:", ", ".join(sorted(sections.keys())))
