# Alumni Webapp Setup Guide

This guide provides a detailed, step-by-step walkthrough for setting up and running the Alumni Database web application, based on the instructions in the `README.md`. It includes more granular instructions for the database setup in MySQL Workbench.

## Part 1: Python Environment Setup

Before touching the database, let's get the Python environment ready.

1.  **Open a terminal or command prompt** in the project's root directory (`Alumni-Database-Webapp`).
2.  **Create a virtual environment:** This creates an isolated space for this project's Python packages.
    ```bash
    python -m venv venv
    ```
3.  **Activate the virtual environment:**
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
    You will know it's active because your command prompt will be prefixed with `(venv)`.
4.  **Install required packages:**
    ```bash
    .\venv\Scripts\activate
    ```

## Part 2: MySQL Workbench Step-by-Step

This section breaks down the database setup from the `README.md` into explicit actions.

### Step 2.1: Open and Connect to MySQL Workbench
1.  Launch the MySQL Workbench application.
2.  On the welcome screen, under "MySQL Connections", click on your local connection (it is usually named `Local instance 80` or something similar).
3.  If it asks for a password, enter the root password you set when you installed MySQL.

### Step 2.2: Create and Populate the Databases
You will run the SQL script files provided in the `Dump Files` directory.

1.  **Load the `users` database script:**
    *   In the top menu, click `File` -> `Open SQL Script...`.
    *   Navigate to the `Alumni-Database-Webapp` project folder, then into `Dump Files`.
    *   Select `users_database_dump.sql` and click `Open`.
2.  **Run the `users` script:**
    *   A new tab will open showing the SQL commands.
    *   In the toolbar for this script tab, click the **first lightning bolt icon** (the one that executes the entire script, not the one with a cursor icon).
    *   Check the "Action Output" panel at the bottom. You should see green checkmarks indicating success.
3.  **Load the `alumni` database script:**
    *   Go back to the top menu: `File` -> `Open SQL Script...`.
    *   This time, select `database_dump.sql` and click `Open`.
4.  **Run the `alumni` script:**
    *   Just as before, click the **first lightning bolt icon** to execute the script. This one might take a bit longer as it's a larger file.
5.  **Verify the databases:**
    *   In the left-hand "Navigator" panel, select the **"Schemas"** tab.
    *   You should now see `alumni` and `users` in the list of databases. If not, right-click in the empty space of the Schemas panel and click `Refresh All`.

### Step 2.3: Create the `student` and `employee` Users
Follow the `README.md` instructions for creating users. Here is a more detailed breakdown of the clicks:

1.  In the "Navigator" panel, click the **"Administration"** tab (it's next to "Schemas").
2.  Under "Instance", click **"Users and Privileges"**.
3.  Click the **"Add Account"** button at the bottom.
4.  **For the `student` user:**
    *   **Login Name:** `student`
    *   **Authentication Type:** Keep as `Standard`
    *   **Password:** `Pass@1234`
    *   **Confirm Password:** `Pass@1234`
    *   Click **"Apply"**.
5.  **For the `employee` user:**
    *   Click **"Add Account"** again.
    *   **Login Name:** `employee`
    *   **Password:** `Pass@5678`
    *   **Confirm Password:** `Pass@5678`
    *   Click **"Apply"**.

### Step 2.4: Grant Permissions to the New Users
Now you will run the final two SQL scripts.

1.  **Load the `student` permissions script:**
    *   Go to `File` -> `Open SQL Script...`.
    *   Select `student_role_permissions.sql` and click `Open`.
2.  **Run the `student` permissions script:**
    *   Click the **first lightning bolt icon** to execute it.
3.  **Load the `employee` permissions script:**
    *   Go to `File` -> `Open SQL Script...`.
    *   Select `employee_role_permissions.sql` and click `Open`.
4.  **Run the `employee` permissions script:**
    *   Click the **first lightning bolt icon** to execute it.

The database is now fully configured.

## Part 3: Configure and Run the App

1.  **Edit the `credentials.yaml` file:**
    *   Open `credentials.yaml` in a text editor.
    *   Change the value for `mysql_password1:` from `Joy@2003` to your actual MySQL root password.
    *   The other passwords (`mysql_password2` and `mysql_password3`) should already be correct (`Pass@1234` and `Pass@5678`).
2.  **Run the application:**
    *   Go back to your terminal where the `(venv)` is active.
    *   Execute the command:
        ```bash
        python app.py
        ```
3.  **Access the webapp:**
    *   Open your web browser and navigate to `http://127.0.0.1:4999`.

You can now log in using the credentials from the `users` table, such as `Piyush` / `pass123` for an admin account.
