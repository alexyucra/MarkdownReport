#!/usr/bin/env python3

# Command line flags

import argparse

parser = argparse.ArgumentParser(description='Converts Markdown to elegant PDF reports')
parser.add_argument('--basic', dest='basic', action='store_true',
    help='Do not enrich HTML with LaTeX and syntax highlighting (faster builds)')
parser.add_argument('--watch', dest='watch', action='store_true',
    help='Watch the current folder for changes and rebuild automatically')
parser.add_argument('--quiet', dest='quiet', action='store_true',
    help='Do not output any information')
parser.add_argument("--timeout", type=int, default=2,
    help='Page generation timeout')
parser.set_defaults(watch=False)
args = parser.parse_args()

from weasyprint import HTML

from shutil import copyfile
from distutils.dir_util import copy_tree
from tempfile import gettempdir
from time import time, sleep
from sys import stdout, stderr
import subprocess
import re, glob, os

# Check directory

ok = False
for file in os.listdir("."):
    if file.endswith(".md"):
        ok = True
        break
if not ok:
    stderr.write("No markdown file found in the current folder")
    exit(1)

script_path = os.path.dirname(os.path.realpath(__file__))

# Temp dir

timestamp = str(int(time()))
tmp_dir = gettempdir() + "/" + timestamp + "_md-report/"
os.makedirs(tmp_dir, exist_ok=True)

# Headless browser

if not args.basic:
    from playwright.sync_api import sync_playwright

prev_compile_time = 0
def recompile(notifier):
    if notifier is not None and (notifier.maskname != "IN_MODIFY" or notifier.pathname.endswith(".pdf")):
        return
    global prev_compile_time
    if time() - prev_compile_time < 1:
        return
    prev_compile_time = time()

    if not args.quiet:
        stdout.write("\rBuilding the PDF file...")
        stdout.flush()

    try:
        # Limpar arquivos temporários
        files = glob.glob(tmp_dir + '/*.md')
        for f in files:
            os.remove(f)

        # Debug: mostrar diretório de trabalho atual
        if not args.quiet:
            stdout.write(f"\rCurrent working directory: {os.getcwd()}\n")
            stdout.flush()

        # Preparar arquivos
        copyfile(script_path + "/base.html", tmp_dir + "/base.html")
        if not os.path.islink(tmp_dir + "/src"):
            os.symlink(script_path + "/src", tmp_dir + "/src")
        copy_tree(".", tmp_dir)

        # Markdown parsing
        subprocess.check_output(script_path + "/md-parsing " + tmp_dir, shell=True)
        html_file_name = tmp_dir + "output.html"

        # Interpret JS code
        if not args.basic:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto("file://" + os.path.abspath(html_file_name))
                page.wait_for_load_state('networkidle')
                interpreted_html = page.content()
                browser.close()

                with open(html_file_name, "w") as html_out_file:
                    html_out_file.write(interpreted_html)

        # Create final PDF file
        pdf = HTML(html_file_name).write_pdf()
        
        # Usar caminho absoluto para o diretório output
        output_dir = os.path.abspath('/app/output')  # Garantir caminho absoluto
        output_path = os.path.join(output_dir, 'output.pdf')
        
        # Debug: mostrar caminhos e permissões
        if not args.quiet:
            stdout.write(f"\rOutput dir: {output_dir}\n")
            stdout.write(f"\rOutput path: {output_path}\n")
            stdout.write(f"\rDirectory exists: {os.path.exists(output_dir)}\n")
            if os.path.exists(output_dir):
                stdout.write(f"\rDirectory permissions: {oct(os.stat(output_dir).st_mode)[-3:]}\n")
            stdout.write(f"\rDirectory listing:\n")
            stdout.write(subprocess.check_output(['ls', '-la', '/app']).decode())
            stdout.flush()
        
        # Criar diretório output se não existir
        os.makedirs(output_dir, exist_ok=True)
        os.chmod(output_dir, 0o777)  # Garantir permissões totais
        
        # Debug: verificar após criar diretório
        if not args.quiet:
            stdout.write(f"\rAfter mkdir - Directory exists: {os.path.exists(output_dir)}\n")
            stdout.write(f"\rAfter mkdir - Permissions: {oct(os.stat(output_dir).st_mode)[-3:]}\n")
            stdout.flush()
        
        # Tentar salvar o arquivo várias vezes se necessário
        max_retries = 3
        retry_delay = 1  # segundos
        
        for attempt in range(max_retries):
            try:
                # Debug: tentar criar arquivo vazio primeiro
                with open(output_path, 'wb') as f:
                    f.write(pdf)
                if not args.quiet:
                    stdout.write(f"\rFile created successfully\n")
                    stdout.flush()
                break
            except FileNotFoundError as e:
                if not args.quiet:
                    stdout.write(f"\rAttempt {attempt + 1}: Error - {str(e)}\n")
                    stdout.write(f"\rTrying to create directory again...\n")
                    stdout.flush()
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                if attempt == max_retries - 1:
                    raise
                sleep(retry_delay)
                continue
            except Exception as e:
                if not args.quiet:
                    stderr.write(f"\rUnexpected error: {str(e)}\n")
                    stderr.flush()
                raise

        if not args.quiet:
            stdout.write("\rDone.                   \n")
            stdout.flush()

    except Exception as e:
        if not args.quiet:
            stderr.write(f"\rError: {str(e)}\n")
            stderr.flush()
        return

recompile(None)

if not args.watch:
    exit(0)

import pyinotify

watch_manager = pyinotify.WatchManager()
event_notifier = pyinotify.Notifier(watch_manager, recompile)

watch_manager.add_watch(os.path.abspath("."), pyinotify.ALL_EVENTS, rec=True)
event_notifier.loop()

exit(0)
