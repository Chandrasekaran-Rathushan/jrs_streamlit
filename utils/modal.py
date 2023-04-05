import streamlit as st
from streamlit.components.v1 import html

class Modal:
    def __init__(self, title, show_footer, show_close_header_btn, height=100):
        self.title = title
        self.show_footer = show_footer
        self.show_close_header_btn = show_close_header_btn
        self.height = height

        self.body = ''
        self.modal_html = ''
        self.temp_modal_html = ''

    def init_modal(self):
        return f"""
            <div class="modal fade" 
                id="staticBackdrop" 
                data-bs-backdrop="static" 
                data-bs-keyboard="false" 
                tabindex="-1" 
                aria-labelledby="staticBackdropLabel" 
                aria-hidden="true"
                style="position: relative; z-index: 1055;"
                >
                <div class="modal-dialog">
                    <div class="modal-content">
                        {self.header}
                        {self.body_context}
                        {self.footer}
                    </div>
                </div>
            </div>
        """

    def create_modal_header(self):
        close_btn = ""

        if self.show_close_header_btn:
            close_btn = """<button type='button' class='btn-close' data-bs-dismiss='modal' aria-label='Close'></button>"""

        return f"""
            <div class='modal-header'>
                <h1 class='modal-title fs-5' id='staticBackdropLabel'>{self.title}</h1>
                {close_btn}
            </div>
        """

    def create_modal_body(self, context):
        return f"""
            <div class='modal-body'>
                {context}
            </div>
        """
    
    def create_modal_footer(self):
        if self.show_footer:
            return """
                <div class='modal-footer'>
                    <button type='button' class='btn btn-secondary' data-bs-dismiss='modal'>Close</button>
                    <button type='button' class='btn btn-primary'>Ok</button>
                </div>
            """
        
        return ""
    
    def open(self):
        self.modal_html = self.temp_modal_html
    
    def close(self):
        self.temp_modal_html = self.modal_html
        self.modal_html.empty()

    
    def show_modal(self):
       # Open the modal
        
        self.header = self.create_modal_header()
        self.body_context =  self.create_modal_body(context=self.body)
        self.footer = self.create_modal_footer()

        self.skelton = self.init_modal()

        modal_handle_script = """
            document.addEventListener("DOMContentLoaded", function() {
                $('#staticBackdrop').modal('show');
                $('.modal-backdrop').remove();
            });
        """

        body_css = """
                {
                    margin: 0px;
                    font-family: var(--bs-body-font-family);
                    font-size: var(--bs-body-font-size);
                    font-weight: var(--bs-body-font-weight);
                    line-height: var(--bs-body-line-height);
                    color: var(--bs-body-color);
                    text-align: var(--bs-body-text-align);
                    background-color: transparent;
                    text-size-adjust: 100%;
                    -webkit-tap-highlight-color: transparent;
                    }
                """

        self.modal_html = html(
            f"""
            <script 
                src='https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.4/jquery.min.js' 
                integrity='sha512-pumBsjNRGGqkPzKHndZMaAG+bir374sORyzM3uulLV14lN5LyykqNk8eEeUlUkB3U0M4FApyaHraT65ihJhDpQ==' 
                crossorigin='anonymous' 
                referrerpolicy='no-referrer'>
            </script>

            <link 
                href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css' 
                rel='stylesheet' 
                integrity='sha384-GLhlTQ8iRABdZLl6O3oVMWSktQOp6b7In1Zl3/Jr59b6EGGoI1aFkw7cmDA6j6gD' 
                crossorigin='anonymous'
                >

            <script 
                src='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js' 
                integrity='sha384-w76AqPfDkMBDXo30jS1Sgez6pr3x5MlQ1ZAGC+nuZB+EYdgRZgiwxhTBTkF7CXvN' 
                crossorigin='anonymous'>
            </script>

            <script 
                type='text/javascript'>
                {modal_handle_script}
            </script>
            <style>
                body {
                    body_css
                }
            </style>
            {self.skelton}
            """,
            height=self.height)
        
        


    def add_element(self, element):
        # Add an element to the modal body
        self.body = self.body + element
