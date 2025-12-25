import modal
import inspect

print("Modal version:", modal.__version__)
print("\nDir(modal):")
print(dir(modal))

print("\nModal.__all__:")
try:
    print(modal.__all__)
except AttributeError:
    print("No __all__ defined")

print("\nChecking for Mount:")
if hasattr(modal, "Mount"):
    print("modal.Mount exists")
else:
    print("modal.Mount DOES NOT exist")

try:
    from modal import Mount
    print("from modal import Mount WORKS")
except ImportError as e:
    print(f"from modal import Mount FAILED: {e}")
