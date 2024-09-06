# Contributing to Blackboard Sync

> [!NOTE]
> For university support contributions, see
> [UNIVERSITIES.md](UNIVERSITIES.md) instead.


So, you want to contribute to Blackboard Sync?

You are in the right place.


## Which way to go?

Create an [Issue](new-issue) if:
- You have found a bug in the app.
- You have a feature request.

Instead create a [Pull Request](new-pr) if:
- You have fixed a bug in the app.
- You have created a feature for the app.

Keep in mind it is always better to ask if a certain feature is
within the development roadmap before working on it.


## Contributing via Issues

Please ensure your description is clear and has sufficient
instructions to be able to reproduce the issue.

A bug report form is available to help you with this.

### Feature Request

Great feature requests tend to have:

- A quick idea summary.
- What & why you wanted to add the specific feature.

[Open a new issue][new-issue].


## Contributing via Pull Request

1. [Fork](https://github.com/sanjacob/BlackboardSync/fork) the repository.
2. Clone your copy of the repository on your machine:
   `git clone https://github.com/$USER/BlackboardSync.git`.
3. Set up your enviroment using `pipenv`:
   `pipenv install --dev`.
4. Create a new branch to work on a new feature or fix:
   `git switch -c some-feature-you-want`.
5. You can test the project to make sure everything works:
   `pipenv run pytest`.
6. You can perform a real test by running the app:
   `pipenv run python -m blackboard_sync`.
7. Once you are done making the changes you wanted, commit:
   `git add . && git commit`.
8. Push your changes to your copy of the repo on GitHub:
   `git push --set-upstream origin some-feature-you-want`.
9. Create a pull request for your branch:
   `sanjacob/main <- USER/some-feature-you-want`.

Some extra pointers:

- You can test the app even without needing a Blackboard account
  by using our mock instance found under "Fakeboard (dev)" in the
  university list.
- Please do not commit unnecessary files, such as those of your
  text editor, operating system, etc.
- Please only ever modify `Pipfile` and `Pipfile.lock` if your
  changes directly need so.
- Use a sensible feature branch name, PR title, and PR description.


## License

By contributing to BlackboardSync, you agree that your
contributions will be licensed under the LICENSE file in
the root directory of this source tree.


[new-issue]: https://github.com/sanjacob/BlackboardSync/issues/new
[new-pr]: https://github.com/sanjacob/BlackboardSync/pull/new
