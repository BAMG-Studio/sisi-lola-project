import modal
print("Imported modal from:", modal.__file__)
print("Attributes:", dir(modal))
print("Mount exists?", hasattr(modal, 'Mount'))

try:
    from modal import Mount
    print("from modal import Mount succeeded", Mount)
except ImportError as e:
    print("from modal import Mount failed:", e)

try:
    from modal.mount import Mount
    print("from modal.mount import Mount succeeded", Mount)
    print("Has from_local_dir?", hasattr(Mount, 'from_local_dir'))
except ImportError as e:
    print("from modal.mount import Mount failed:", e)
