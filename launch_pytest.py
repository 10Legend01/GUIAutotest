from os.path import dirname, abspath

import pytest
import sys

if __name__ == "__main__":
    args = sys.argv[1:]

    assert len(args) > 1

    args += args.pop().split()

    args[0] = abspath(args[0])

    json_file = ' '.join(args)
    print(json_file)
    sys.exit(pytest.main(
        args=[abspath(dirname(__file__)),
              "--json={}".format(json_file),
              ]))
