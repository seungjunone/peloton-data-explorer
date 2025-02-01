# peloton_workout_analytics
Demo of Peloton data extraction via API calls, data pipelines, etc



# Data Science Handbook

The [Data Science Handbook](https://handbook.datascience.2u.com/) is a collection of information on the data science team at 2U - who we are, what we do, and how we work.

The handbook is written in Markdown and served as a [static website](https://handbook.datascience.2u.com/) hosted using [Github Pages](https://pages.github.com/). We use [MkDocs](https://www.mkdocs.org/) to generate the site from markdown and the popular [Material](https://squidfunk.github.io/mkdocs-material/) theme for the site layout and design.

We encourage you to review the [mkdocs introductory tutorial](https://www.mkdocs.org/getting-started/) and [mkdocs-material getting started](https://squidfunk.github.io/mkdocs-material/getting-started/) page to learn about the technology behind the handbook. These pages will get you up-to-speed on how to install mkdoc, add/modify pages, and serve the pages in a built-in dev-server. Additionally, the [Material reference](https://squidfunk.github.io/mkdocs-material/reference/) page contains code snippets describing how to add diagrams, codeblocks, data tables, and more.

## Hosting

The Data Science Handbook is hosted using Github Pages. The repository is configured to serve the site from the [gh-pages](https://github.com/2uinc/data-science-handbook/tree/gh-pages) branch. See the [repository settings](https://github.com/2uinc/data-science-handbook/settings/pages) to update the configuration.

## Running Quick Guides on Jupyter Notebook

The quick-guides contains individual walkthrough that you can follow along on your machine. From terminal, 

1. Clone this repo and navigate to it.
1. `python3 -m venv .python` Create a virtual environment 
1. `source .python/bin/activate` Activate viertual environment created above
1. `pip install -r requirements.txt` Upgrade pip, the Python package installer, to the latest version within the activated virtual environment 
1. `pip install -r requirements.txt` Installs all the Python packages listed in the requirements.txt file within the activated virtual environment 
1. `Jupyter Notebook` Start the web server to run the notebook locally. By default, this will open the browser with Jupyter Notebook interface.

In quick-guides notebooks, Peloton credentials are loaded from environmental variable. You could save them locally in .bash_profile, and define it there.

To open `bash_profile` in Visual Studio:
```
code ~/.bash_profile
```

And add peloton credentials to bash_profile.
```
export peloton_user_name="{ your username }"
export peloton_password="{ your password }"
```


See the [Makefile](./Makefile) for shell commands that simplify the process of building and serving the site. For example, run
```Bash
make open-dev-server
```
to build and serve the site.

Alternatively you can build and serve the site using Docker. In order to enable plugins a custom image must be built. 

1. Build the custom image:

```Bash
make build-custom-image
```

2. Build the site:

```Bash
make build-site-custom-image
```

3. Serve the site:

```Bash
make serve-site-custom-image
```

## How do I update the Data Science Handbook?

To add a page, create a markdown file, place it in `/docs` folder, and map it in [mkdocs.yml](./mkdocs.yml). To update a page, update the corresponding markdown file.

Once PR is approved and merged to `main` branch, the change will automatically be reflected in github page [Github Actions](https://squidfunk.github.io/mkdocs-material/publishing-your-site/#with-github-actions).

Please read the [handbook guide](https://handbook.datascience.2u.com/guide/) before submitting a PR.
 
For common page types, check the `/templates` directory to find a template that can be copied and easily updated for a new page.
