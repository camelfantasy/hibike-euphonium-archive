# Hibike! Euphonium Archive

This application syncs the structure of a Google Drive folder and all image files to a MongoDB database, and renders it as a user-friendly viewing experience with search and image tag functions.  More details are on the `/flask_app/templates/index.html` page.

Note that this project is still in beta and will see frequent updates and ocassional bugs.

## Installation
This guide assumes little programming or server management knowledge.  Further customization will require some knowledge in programming and web design.

1. Ensure Python is installed and relatively up-to-date.  This application was developed in version 3.9.

2. Install the packages in `requirements.txt` by navigating to the root folder of the application and running:
    ```
    pip3 install -r requirements.txt
    ```

3. [Install](https://www.mongodb.com/try/download/community) MongoDB or [set up](https://www.mongodb.com/cloud/atlas) a cloud server.  Free tiers exist for both and are sufficient for this application.  This application was developed with version v4.4.x.

4. Set configuration values.  These **must** be set for the application to work properly.  Configuration values can be set either as environmental variables (in a file usually found in the home directory) or in `config.py`, with nonempty values in the application config file taking precedence.

    On Mac/Linux, environmental variables are set with `export [VARIABLE_NAME]=[VARIABLE_VALUE]`.  Config file values are placed between the existing quotation or apostrophe marks.

    **`SECRET_KEY`**: In Terminal, generate with:
    ```
    python -c 'import os; print(os.urandom(16))'
    ```
    If using `config.py`, make sure to include the `b''` when setting the variable; it is not needed for an environmental variable.

    **`DRIVE_API_KEY`**: Generate one by following the instructions [here](https://support.google.com/googleapi/answer/6158862).

    **`ROOT_ID`**: This is the folder ID of the root Google Drive folder.  The folder link will look similar to:
    ```
    https://drive.google.com/drive/folders/[FOLDER_ID]
    ```

    **`MONGODB_HOST`**: This is the connection string of the MongoDB database.
    
    For a **locally hosted database**, the connection string will be:
    ```
    mongodb://localhost:27017/[DATABASE_NAME]
    ```
    with `[DATABASE_NAME]` substituted for a name of your choice.
    <br><br>
    For a **cloud-hosted database**, create a new user under `Database Access` and set `Database User Privileges` to `Atlas admin`
    
    Go to `Network Access` and either add the IP address or range of addresses the application will be running from, or select `Allow access from anywhere`.
    
    On the `Clusters` page, select `Connect`, `Connect your application`, `Python` and `3.6 or later`, and copy the connection string.  Paste this into your environmental variable or `config.py`, substituting `<password>` for the one set earlier and `<db_name>` for a name of your choice.

5. Using Terminal, navigate to the root folder of the application.  Do `flask run` and wait for the `Startup successful` message.  If it does not show or errors appear, something was set up incorrectly.

    The link to access the application will appear among the messages, and look similar to `http://127.0.0.1:5000/`.  To stop the application, do `CTRL+C` in Terminal.

### Optional Steps:
1. Google Analytics: Set up using the instructions [here](https://support.google.com/analytics/answer/1008015?hl=en), then substitute in the Tracking ID into `/flask_app/templates/base.html` at this line near the middle of the page: `ga('create', '[TRACKING ID]', 'auto');`.

2. Deployment to Heroku:
* Upload the code to a GitHub repository
* Create a new application on Heroku (a free tier exists and is sufficient), and connect the repository under `Deploy`.
* Set the above environmental variables in `Config Vars` under `Settings`.  Additionally, set `SITE_URL` to your site URL.
* Click `More` and `Restart all dynos` for the changes to take effect, and click `Open app` to access the application.
* If the application does not start up, check for errors in `View logs` under `More`.

## Permissions

The application follows a basic permission system.  No account is required for actions related to accessing images and folders, creating an account, or using the unrestricted API routes.
<table>
	<th width="60%">Permission</th>
	<th width="10%">User</th>
	<th width="10%">Mod</th>
	<th width="10%">Admin</th>
	<th width="10%">Root</th>
	<tr>
		<td>
			Change own password
		</td>
		<td style="color:green">Y</td>
		<td style="color:green">Y</td>
		<td style="color:green">Y</td>
		<td style="color:green">Y</td>
	<tr>
		<td>
			Delete own account
		</td>
		<td style="color:green">Y</td>
		<td style="color:green">Y</td>
		<td style="color:green">Y</td>
		<td style="color:red">N</td>
	<tr>
		<td>
			Favorite images
		</td>
		<td style="color:green">Y</td>
		<td style="color:green">Y</td>
		<td style="color:green">Y</td>
		<td style="color:green">Y</td>
	</tr>
	<tr>
		<td>
			Add/remove existing image tags to/from images and all images in a folder
		</td>
		<td style="color:red">N</td>
		<td style="color:green">Y</td>
		<td style="color:green">Y</td>
		<td style="color:green">Y</td>
	</tr>
        <td>
            Set/delete API key
        </td>
        <td style="color:red">N</td>
        <td style="color:green">Y</td>
            <td style="color:green">Y</td>
        <td style="color:green">Y</td>
	</tr>
	<tr>
		<td>
			Delete/edit User accounts
		</td>
		<td style="color:red">N</td>
		<td style="color:green">Y</td>
		<td style="color:green">Y</td>
		<td style="color:green">Y</td>
	</tr>
	<tr>
		<td>
			Add new image tags to images and all images in a folder
		</td>
		<td style="color:red">N</td>
		<td style="color:red">N</td>
		<td style="color:green">Y</td>
		<td style="color:green">Y</td>
	</tr>
	<tr>
		<td>
			Add/delete/recategorize tags from the Tags page
		</td>
		<td style="color:red">N</td>
		<td style="color:red">N</td>
		<td style="color:green">Y</td>
		<td style="color:green">Y</td>
	</tr>
	<tr>
		<td>
			Sync Google Drive to database
		</td>
		<td style="color:red">N</td>
		<td style="color:red">N</td>
		<td style="color:green">Y</td>
		<td style="color:green">Y</td>
	</tr>
	<tr>
		<td>
			Use restricted API routes
		</td>
		<td style="color:red">N</td>
		<td style="color:red">N</td>
		<td style="color:green">Y</td>
		<td style="color:green">Y</td>
	</tr>
	<tr>
		<td>
			Delete/edit Mod accounts
		</td>
		<td style="color:red">N</td>
		<td style="color:red">N</td>
		<td style="color:green">Y</td>
		<td style="color:green">Y</td>
	</tr>
	<tr>
		<td>
			Delete/edit Administrator accounts
		</td>
		<td style="color:red">N</td>
		<td style="color:red">N</td>
		<td style="color:red">N</td>
		<td style="color:green">Y</td>
	</tr>
</table>

## Future development

Development is currently still in beta.  The full release at an undetermined point in the future will include more features and improvements that will improve user experience.  These are likely (but not guaranteed) to include:
* Increasing the efficiency of certain functions related to retrieving database information due to MongoEngine limitations.
* Embedding other file types
* Adding an album view for pages with multiple images.
* Implementing favorite counts and tag counts/similarity into various functions.
* Annotated images.
* Some support for Japanese and other languages.