mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = fabricio.bucher@gmail.com\"\n\
" > ~/.streamlit/credentials.toml

echo "
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml