# VEST Squad WatsonX Challenge

This repo contains a simple example of integrating a Python back-end with a JS front-end using IBM's UI library. Technologies used include:

- [Flask](https://flask.palletsprojects.com/en/2.3.x/)
- [Svelte](https://svelte.dev/)
- [Carbon UI](https://carbon-components-svelte.onrender.com/)

## Design

For the design of this application, the Flask back-end contains both REST APIs as well as some paths to serve static assets. This means that after the static assets of the Svelte front-end have been built they are served via the Flask back-end.

Lastly, the top-level `package.json` facilitates a simpler DX while working. It uses an [NPM workspace](https://docs.npmjs.com/cli/v7/using-npm/workspaces) to quickly call scripts that the front-end client contains.

## Getting started

Begin by running

```bash
npm ci
```

This will install all of the dependencies for both the Svelte front-end and the Python backend

> Please note the `preinstall` script in the top-level `package.json` in this repository. If this command, or any other python-related command, fails you may need to add an alias to your shell config.

After installing all the dependencies you can run

```bash
npm run dev
```

With this, the development version of the client should now be live at `http://localhost:5173/`.

> Note that the development version of the server will be hosted on port 5001. Backend API requests to `/api/*` will be proxied via the vite dev server.

You also have the option to run

```bash
npm run dev-static
```

Much like the previous command it will stand up a development instance of the back-end service at port 5001, however, instead of serving the front-end via the vite dev server the back-end instead serves the static files and will rebuild them on any changes. 

> Any changes made to the client application will result in an automatic rebuild, however, if viewing the webpage you will need to refresh to see changes.

## Deployment

A simple `Dockerfile` as well as a bash script to build an image has also been included in this repository if you wish to deploy via Docker.

The `Docker` file will copy only what's needed to deploy the app (the `/client/dist` folder, `/server` folder, and `requirements.txt`) and expose the default port Flask uses.

The default image name that will be generated is the same as the package name in the `package.json`.

There are some docker utility commands in `package.json` as well, such as:
- `npm run docker:build` to build a docker image
- `npm run docker:run` to start the image, and open localhost in the browser
- `npm run docker:clean` to remove containers using image, image itself, and dangling images

## Slack App testing for local development:

- Get latest slack env values from 1Password
- Join the [team hackathon slack](https://join.slack.com/t/resell-lab-ibm/shared_invite/zt-20ehtfi1f-1zUl2F6_xlV0NS7EDeJSVg)
- Join the workspace channel `hackathon-bot`
- Start the Flask app and slack app with `npm run dev`
- Try:
  - Mention the bot with `@resell-bot` in the hackathon-bot slack channel and looking at server logs to see how everything works.
  - Slash command `/resell`
  - Open the resell-bot home page
