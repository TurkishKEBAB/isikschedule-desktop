"""PyCharm cache invalidation script."""
import os
import shutil
import sys

def clear_pycharm_caches():
    """Clear PyCharm caches to fix import issues."""
    base_dir = os.path.dirname(os.path.abspath(__file__))

    paths_to_clear = [
        os.path.join(base_dir, '__pycache__'),
        os.path.join(base_dir, '.pytest_cache'),
        os.path.join(base_dir, 'algorithms', '__pycache__'),
        os.path.join(base_dir, 'core', '__pycache__'),
        os.path.join(base_dir, 'utils', '__pycache__'),
        os.path.join(base_dir, 'gui', '__pycache__'),
        os.path.join(base_dir, 'reporting', '__pycache__'),
        os.path.join(base_dir, 'config', '__pycache__'),
    ]

    cleared = []
    for path in paths_to_clear:
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                cleared.append(path)
                print(f"✓ Cleared: {path}")
            except Exception as e:
                print(f"✗ Failed to clear {path}: {e}")

    if cleared:
        print(f"\n✓ Successfully cleared {len(cleared)} cache directories")
        print("\nPlease restart PyCharm for changes to take effect.")
        print("File -> Invalidate Caches -> Just Restart")
    else:
        print("No caches found to clear")

if __name__ == "__main__":
    clear_pycharm_caches()

