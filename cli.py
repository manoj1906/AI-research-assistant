#!/usr/bin/env python3
"""
Command Line Interface for AI Research Assistant
"""

from src.config import Config
from src.research_assistant import ResearchAssistant
import click
import sys
from pathlib import Path
import json

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))


@click.group()
@click.option('--config', '-c', help='Configuration file path')
@click.pass_context
def cli(ctx, config):
    """AI Research Assistant CLI"""
    ctx.ensure_object(dict)

    # Initialize config
    if config:
        ctx.obj['config'] = Config.from_file(config)
    else:
        ctx.obj['config'] = Config()

    # Initialize assistant
    ctx.obj['assistant'] = ResearchAssistant(ctx.obj['config'])


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--paper-id', help='Custom paper ID')
@click.pass_context
def upload(ctx, file_path, paper_id):
    """Upload and process a research paper"""
    assistant = ctx.obj['assistant']

    try:
        click.echo(f"📄 Processing paper: {file_path}")
        result_id = assistant.upload_paper(file_path, paper_id)
        click.echo(f"✅ Paper uploaded successfully with ID: {result_id}")
    except Exception as e:
        click.echo(f"❌ Error processing paper: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('question')
@click.option('--paper-id', help='Specific paper ID to query')
@click.option('--section', help='Specific section to focus on')
@click.option('--format', 'output_format',
              type=click.Choice(['text', 'json']),
              default='text',
              help='Output format')
@click.pass_context
def ask(ctx, question, paper_id, section, output_format):
    """Ask a question about research papers"""
    assistant = ctx.obj['assistant']

    try:
        click.echo(f"❓ Question: {question}")
        answer = assistant.ask_question(question, paper_id, section)

        if output_format == 'json':
            result = {
                'question': question,
                'answer': answer.answer,
                'confidence': answer.confidence,
                'evidence': answer.evidence,
                'context': answer.context
            }
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(f"\\n📝 Answer: {answer.answer}")
            if answer.evidence:
                click.echo(f"\\n🔍 Evidence: {answer.evidence}")
            click.echo(f"\\n📊 Confidence: {answer.confidence:.2f}")

    except Exception as e:
        click.echo(f"❌ Error answering question: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--paper-id', help='Specific paper ID')
@click.option('--section', help='Specific section to summarize')
@click.pass_context
def summarize(ctx, paper_id, section):
    """Generate a summary of a paper or section"""
    assistant = ctx.obj['assistant']

    if not paper_id:
        papers = assistant.list_papers()
        if not papers:
            click.echo("❌ No papers found. Upload a paper first.", err=True)
            sys.exit(1)
        paper_id = papers[0]['id']  # Use first paper

    try:
        click.echo(f"📄 Summarizing paper {paper_id}" +
                   (f" section {section}" if section else ""))
        summary = assistant.summarize_paper(paper_id, section)
        click.echo(f"\\n📝 Summary:\\n{summary}")

    except Exception as e:
        click.echo(f"❌ Error generating summary: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--format', 'output_format',
              type=click.Choice(['text', 'json']),
              default='text',
              help='Output format')
@click.pass_context
def list_papers(ctx, output_format):
    """List all uploaded papers"""
    assistant = ctx.obj['assistant']

    try:
        papers = assistant.list_papers()

        if output_format == 'json':
            click.echo(json.dumps(papers, indent=2))
        else:
            if not papers:
                click.echo("📚 No papers uploaded yet.")
            else:
                click.echo(f"📚 {len(papers)} papers found:")
                for i, paper in enumerate(papers, 1):
                    click.echo(f"  {i}. {paper['title']} (ID: {paper['id']})")
                    if paper.get('authors'):
                        click.echo(
                            f"     Authors: {', '.join(paper['authors'])}")

    except Exception as e:
        click.echo(f"❌ Error listing papers: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('paper_id')
@click.pass_context
def analyze(ctx, paper_id):
    """Analyze the contribution of a paper"""
    assistant = ctx.obj['assistant']

    try:
        click.echo(f"📊 Analyzing paper {paper_id}...")
        analysis = assistant.analyze_contribution(paper_id)

        click.echo("\\n📝 Analysis Results:")
        for key, value in analysis.items():
            click.echo(f"  {key}: {value}")

    except Exception as e:
        click.echo(f"❌ Error analyzing paper: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def web(ctx):
    """Launch the web interface"""
    import subprocess
    import os

    try:
        # Get the directory of this script
        script_dir = Path(__file__).parent
        app_path = script_dir / "app.py"

        click.echo("🌐 Launching web interface...")
        click.echo("🔗 Access the app at: http://localhost:8501")

        # Launch streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            str(app_path),
            "--server.port", "8501"
        ])

    except Exception as e:
        click.echo(f"❌ Error launching web interface: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
