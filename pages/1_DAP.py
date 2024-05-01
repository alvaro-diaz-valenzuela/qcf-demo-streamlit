import pandas as pd
import streamlit as st
from PIL import Image
import requests

from models.data_types import (
    Product,
    TypeLeg,
    Bank
)
from models.operations import OperationDaily

st.set_page_config(
    page_title="New Operation",
    page_icon=Image.open('./assets/favicon-32x32.png'),
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None,
)

st.title("DAP")

