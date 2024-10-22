from textwrap import dedent

body_template = dedent("""
    <html>
      <head>
        <title>{title}</title>
        <meta name="viewport"
              content="width=device-width, initial-scale=1" />
        <script>
        const openShare = () => {{
          if(navigator.share) {{
            navigator.share({{
              title: '{title}',
              text: '{body_text}'
            }}).catch(console.error);
          }}
        }}

        document.addEventListener('DOMContentLoaded', function() {{
          const shareButton = document.getElementById('share-button');
          shareButton.style.display = (navigator.share) ? 'block' : 'none';
        }});
        </script>
        <style>
          :root {{ color-scheme: light dark; }}
          html {{ height: 100%; background-color: #212121; }}
          body {{
            height: calc(100% - 8rem);
            display: flex;
            flex-flow: column nowrap;
            align-items: flex-start;
            justify-content: stretch;
            margin: 2rem;
            padding: 2rem;
            border-radius: 1.5rem;
            box-shadow: 0px 2px 10px 2px black;
            background-color: light-dark(white, #212121);
            font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
            line-height: 1.5;
          }}
          header {{
            display: flex;
            flex-flow: row nowrap;
            justify-content: space-between;
            align-items: center;
            width: 100%;
          }}
          header > h2 {{ flex: 1; }}
          main {{ flex: 1; }}
          footer {{
            display: flex;
            flex-flow: column nowrap;
            align-self: center;
            align-items: center;
            font-size: 0.75rem;
            color: grey;
          }}
          footer > p {{ margin: 0.25rem; }}
          footer > a {{
            text-decoration: none;
            color: #a02c2c;
          }}
          ul#sharing {{
            display: flex;
            flex-flow: row nowrap;
            justify-content: center;
            margin: 0;
            padding: 0;
            grid-gap: 2rem;
          }}
          ul#sharing > li {{ list-style-type: none; }}
          ul#sharing svg {{
            fill: light-dark(black, white);
            cursor: pointer;
          }}
          #share-button {{ display: none; }}
        </style>
      </head>
      <body>
        <header>
          <h2>{title}</h2>
          <ul id="sharing">
            <li>
              <a href="mailto:?subject={title}&body={body_text}">
                <svg xmlns="http://www.w3.org/2000/svg"
                     viewBox="0 0 16 16" width="16" height="16">
                  <path d="M1.75 2h12.5c.966 0 1.75.784 1.75 1.75v8.5A1.75
                           1.75 0 0 1 14.25 14H1.75A1.75 1.75 0 0 1 0
                           12.25v-8.5C0 2.784.784 2 1.75 2ZM1.5 12.251c0
                           .138.112.25.25.25h12.5a.25.25 0 0 0
                           .25-.25V5.809L8.38 9.397a.75.75 0 0 1-.76 0L1.5
                           5.809v6.442Zm13-8.181v-.32a.25.25 0 0
                           0-.25-.25H1.75a.25.25 0 0
                           0-.25.25v.32L8 7.88Z"></path></svg>
              </a>
            </li>
            <li id="share-button" onClick="openShare()">
              <svg xmlns="http://www.w3.org/2000/svg"
                   viewBox="0 0 16 16" width="16" height="16">
                <path d="M15 3a3 3 0 0 1-5.175 2.066l-3.92 2.179a2.994 2.994
                         0 0 1 0 1.51l3.92 2.179a3 3 0 1 1-.73
                         1.31l-3.92-2.178a3 3 0 1 1 0-4.133l3.92-2.178A3
                         3 0 1 1 15 3Zm-1.5 10a1.5 1.5 0 1 0-3.001.001A1.5
                         1.5 0 0 0 13.5 13Zm-9-5a1.5 1.5 0 1 0-3.001.001A1.5
                         1.5 0 0 0 4.5 8Zm9-5a1.5 1.5 0 1 0-3.001.001A1.5
                         1.5 0 0 0 13.5 3Z"></path></svg>
            </li>
          </ul>
        </header>
        <main>{body_html}</main>
        <footer>
          <p>You may have to configure your browser to open
          attachments with the right application instead of downloading
          them again.</p>
          <p>Content downloaded by
          <a href="https://bbsync.app">Blackboard Sync</a></p>
        </footer>
      </body>
    </html>""").lstrip()


def create_body(title: str, body_html: str, body_text: str) -> str:
    return body_template.format(title=title,
                                body_html=body_html,
                                body_text=body_text)
