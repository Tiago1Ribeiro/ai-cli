from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()

md_text = """
# Heading

This is a long paragraph that should wrap automatically when inside a panel. It contains **bold** and *italic* text.

- List item 1
- List item 2

```python
print("Code block")
```
"""

# Case 1: Direct Nesting (Full Width)
console.print(Panel(Markdown(md_text), title="Direct Nesting (Full Width)"))

# Case 2: Restricted Width Panel
console.print(Panel(Markdown(md_text), title="Restricted Width (50 chars)", width=50))

# Case 3: "Max Width" Logic (Manual)
# Rich Panel 'width' implies fixed width. If we want "Max 80 but shrink if smaller", 
# we usually rely on the terminal size or use a layout. But Panel(expand=False) wraps content.
# For Markdown (which expands), we usually want "Fill up to X".
width = min(console.width, 80)
console.print(Panel(Markdown(md_text), title=f"Adaptive Width (Max 80, Current {width})", width=width))
