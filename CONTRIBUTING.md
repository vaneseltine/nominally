# Contributing

When contributing to this repository, please first discuss the change you wish
to make via issue, email, or some other method before trying to make a change.

Please follow nominally's Code of Conduct in all project interactions.

## Suggested Workflow

1. Open an issue.

1. Fork nominally to your own repository.

1. Then something like:

    ```
    $ git clone git@github.com:yournamehere/nominally.git
    $ cd nominally
    $ python -m venv .venv
    $ source ./.venv/bin/activate
    (.venv) $ python -m pip install -r requirements/dev.txt
    (.venv) $ git checkout -b informative-branch-name
    (.venv) $ nox
    ```
1. Fix things up.

1. Ensure nox is still happy.

1. Leave an explanatory commit message that tags the relevant issue.

1. Push up to your own branch.

1. Open a pull request on GitHub.
