from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
import yaml

# Desc: Utility functions for the webapp