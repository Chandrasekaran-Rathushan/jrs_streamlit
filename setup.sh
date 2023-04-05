mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"rathushan.20191029@iit.ac.lk\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml