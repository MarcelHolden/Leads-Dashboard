"""
Custom css for streamlit app.
"""

main_styles = """
    <style>
    #MainMenu {visibility: hidden;}
    
    footer {visibility: hidden;}
    
    header {visibility: hidden; height:0;}
    
    .block-container {
      margin-top: 0;
      padding-top: 0;
    }
    
    .stMetric {
       background-color: #cce3de;
       # border: 1px solid rgba(28, 131, 225, 0.5);
       padding: 5% 5% 5% 10%;
       border-radius: 10px;
       color: rgb(30, 103, 119);
       overflow-wrap: break-word;
       height: 100px;
    }
    
    [data-testid="stAppViewContainer"] > .main {
        background-image: url("https://images.pexels.com/photos/2116721/pexels-photo-2116721.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1");
        background-size: 100vw 100vh;
        background-position: center;  
        background-repeat: no-repeat;
    }
    
    .stPlotlyChart {
     outline: 5px solid white;
     border-radius: 20px;
     # border: 5px solid white;
     box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.20), 0 6px 20px 0 rgba(0, 0, 0, 0.30);
     # background: orange;
     backdrop-filter: blur(5px);
    }
    
    .stForm{
        width: 350px;
        padding: 2rem;
        background-color: #f9f9f9;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        border-radius: 8px;
        margin: 2rem 30vw;
    }
    
    .stImage img{
        border-radius: 10px;
    }
    
    .menu {
        background: orange;
    }
    
    # .stAlertContainer {
    #     width: 350px;
    #     margin: auto 30vw;
    # }
    </style>
"""

menu_bar_styles = """
    <style>
    .menu {
        background: orange !important;
    }
    .nav-justified {
        background: orange;
    }
    </style>
"""


inner_styles = """
    <style>
    [data-testid="stAppViewContainer"] > .main {
        background-image: url("https://images.pexels.com/photos/3588040/pexels-photo-3588040.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1");
        background-image: url("https://images.pexels.com/photos/13623966/pexels-photo-13623966.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1");
        background-image: url("");
        background-size: 100vw 100vh;
        background-position: center;  
        background-repeat: no-repeat;
        # background: gray;
    }
    .stForm{
        width: 100%;
        padding: 2rem;
        background-color: #f9f9f9;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        border-radius: 8px;
        margin: auto;
    }
    </style>
    """


feature_html = """
                <div style="text-align: center; border: 1px solid #bfd5b2; height: 200px; 
                background: #bfd5b2; border-radius: 10px; margin:5px;padding:2px;">
                    <h5>{}</h5>
                    <div style="font-size: 60px;">{}</div>
                    <p>{}</hp>
                </div>
                """
