# **Contributing**

When contributing to this repository, please first discuss the change you wish to make via issue,
email, chat, or any other method with the owners of this repository before making a change.

## Git Flow

The project uses the Git Flow branching model. The main branches are `main` and `develop`. The `main` branch is the production-ready branch, and the `develop` branch is the integration branch.

The branches are used as follows:

* From Feature to Feature: squash and merge
* From Feature to Develop: squash and merge
* From Develop to Main: fast-forward merge
* From Main to Develop: fast-forward merge
* From Hotfix to Main: fast-forward merge

It's important to follow this flow to keep the project organized and to avoid conflicts.

Every time a feature is merged into the `main` branch, a new release should be created with the version number following the [Semantic Versioning](https://semver.org/) guidelines.

Also, the project uses pre-commit hooks to ensure the code quality. You should install them with `pre-commit install`.

## Commits

The project uses the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification. This is a lightweight convention on top of commit messages. It provides an easy set of rules for creating an explicit commit history. This convention dovetails with [SemVer](https://semver.org/), by describing the features, fixes, and breaking changes made in commit messages.

Each commit message should be conceptually unique and should be able to be understood by itself. It should only contain changes related to the name of the commit. If you need to make a commit with multiple changes that are independent (conceptually), you should split it into multiple commits.

## Pull Request Process

### Features

1. Create your Feature Branch (`git checkout feature/{issue-number}-AmazingFeature`)
2. Check that you have installed pre-commit hooks with `pre-commit install`.
3. Check that your branch is up to date with `git pull` and merge if it's necessary with `git merge origin develop`.
4. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
5. Push to the Branch (`git push`)
6. Open a Pull Request to the `develop` branch or to the main epic branch if there's one defined.

### Bug Fixes

Same as Features, but the branch name should be `bugfix/{issue-number}-FixingSomething`.

### Hotfixes

Same as Features, but the branch name should be `hotfix/{issue-number}-FixingSomething`. And the Pull Request should be opened to the `main` branch.

## Issue Report Process

1. Go to the project's issues.
2. Select the template that better fits your issue.
3. Read the instructions carefully and write within the template guidelines.
4. Submit it and wait for support.

## GitHub Projects

You can use GitHub Projects to manage the project's tasks. It's a good way to keep track of the issues and pull requests.
