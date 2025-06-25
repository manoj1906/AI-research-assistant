#!/usr/bin/env python3
"""
CLI Interface for AI Research Assistant
Provides command-line tools for batch processing and analysis
"""

from src.config import Config
from src.research_assistant import ResearchAssistant
import sys
from pathlib import Path
import click
import json
import logging
from typing import List, Optional

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))


# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@click.group()
@click.option('--config', type=click.Path(exists=True), help='Path to config file')
@click.pass_context
def cli(ctx, config):
    """AI Research Assistant CLI - Intelligent analysis of academic papers."""
    ctx.ensure_object(dict)

    # Initialize research assistant
    if config:
        # Load custom config if provided
        with open(config, 'r') as f:
            config_data = json.load(f)
        ctx.obj['assistant'] = ResearchAssistant(Config(**config_data))
    else:
        ctx.obj['assistant'] = ResearchAssistant()

    click.echo("🔬 AI Research Assistant CLI initialized")


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--paper-id', help='Custom paper ID')
@click.option('--analyze', is_flag=True, help='Run analysis after upload')
@click.pass_context
def upload(ctx, file_path, paper_id, analyze):
    """Upload and process a research paper."""

    assistant = ctx.obj['assistant']

    click.echo(f"📄 Uploading paper: {file_path}")

    try:
        processed_paper_id = assistant.upload_paper(file_path, paper_id)
        click.echo(f"✅ Paper uploaded successfully: {processed_paper_id}")

        if analyze:
            click.echo("🔍 Running analysis...")

            # Run contribution analysis
            contribution = assistant.analyze_contribution(processed_paper_id)
            click.echo(
                f"📊 Main contributions: {contribution.get('main_contributions', 'N/A')}")

            # Generate summary
            summary = assistant.summarize_paper(processed_paper_id)
            click.echo(f"📝 Summary: {summary[:200]}...")

    except Exception as e:
        click.echo(f"❌ Error uploading paper: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('question')
@click.option('--paper-id', help='Specific paper ID to query')
@click.option('--section', help='Specific section to focus on')
@click.option('--output', type=click.File('w'), help='Output file for answer')
@click.pass_context
def ask(ctx, question, paper_id, section, output):
    """Ask a question about research papers."""

    assistant = ctx.obj['assistant']

    click.echo(f"❓ Question: {question}")

    try:
        answer = assistant.ask_question(question, paper_id, section)

        result = {
            "question": question,
            "answer": answer.answer,
            "confidence": answer.confidence,
            "evidence": answer.evidence,
            "section": answer.section,
            "page_numbers": answer.page_numbers
        }

        if output:
            json.dump(result, output, indent=2)
            click.echo(f"📝 Answer saved to {output.name}")
        else:
            click.echo(f"💡 Answer: {answer.answer}")
            click.echo(f"🎯 Confidence: {answer.confidence}")
            if answer.evidence:
                click.echo(f"📚 Evidence: {answer.evidence[:200]}...")

    except Exception as e:
        click.echo(f"❌ Error answering question: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('paper_id')
@click.option('--section', help='Specific section to summarize')
@click.option('--output', type=click.File('w'), help='Output file for summary')
@click.pass_context
def summarize(ctx, paper_id, section, output):
    """Generate a summary of a paper or specific section."""

    assistant = ctx.obj['assistant']

    click.echo(f"📄 Summarizing paper: {paper_id}")
    if section:
        click.echo(f"📑 Section: {section}")

    try:
        summary = assistant.summarize_paper(paper_id, section)

        if output:
            output.write(summary)
            click.echo(f"📝 Summary saved to {output.name}")
        else:
            click.echo("📝 Summary:")
            click.echo("=" * 50)
            click.echo(summary)

    except Exception as e:
        click.echo(f"❌ Error generating summary: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('paper_id')
@click.option('--analysis-type', type=click.Choice(['contribution', 'methodology', 'results']),
              default='contribution', help='Type of analysis to perform')
@click.option('--output', type=click.File('w'), help='Output file for analysis')
@click.pass_context
def analyze(ctx, paper_id, analysis_type, output):
    """Analyze paper contributions, methodology, or results."""

    assistant = ctx.obj['assistant']

    click.echo(f"🔍 Analyzing paper: {paper_id}")
    click.echo(f"📊 Analysis type: {analysis_type}")

    try:
        if analysis_type == 'contribution':
            analysis = assistant.analyze_contribution(paper_id)
        elif analysis_type == 'methodology':
            analysis = assistant.analyze_methodology(paper_id)
        elif analysis_type == 'results':
            analysis = assistant.analyze_results(paper_id)

        if output:
            json.dump(analysis, output, indent=2)
            click.echo(f"📝 Analysis saved to {output.name}")
        else:
            click.echo(f"📊 Analysis Results:")
            click.echo("=" * 50)
            for key, value in analysis.items():
                click.echo(f"{key}: {value}")

    except Exception as e:
        click.echo(f"❌ Error analyzing paper: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('paper_ids', nargs=-1, required=True)
@click.option('--aspect', type=click.Choice(['methodology', 'results', 'approach']),
              default='methodology', help='Aspect to compare')
@click.option('--output', type=click.File('w'), help='Output file for comparison')
@click.pass_context
def compare(ctx, paper_ids, aspect, output):
    """Compare multiple research papers."""

    assistant = ctx.obj['assistant']

    click.echo(f"🔍 Comparing papers: {', '.join(paper_ids)}")
    click.echo(f"📊 Comparison aspect: {aspect}")

    try:
        comparison = assistant.compare_papers(list(paper_ids), aspect)

        if output:
            json.dump(comparison, output, indent=2)
            click.echo(f"📝 Comparison saved to {output.name}")
        else:
            click.echo(f"📊 Comparison Results:")
            click.echo("=" * 50)
            click.echo(comparison)

    except Exception as e:
        click.echo(f"❌ Error comparing papers: {e}", err=True)
        sys.exit(1)


@cli.command("list-papers")
@click.pass_context
def list_papers(ctx):
    """List all uploaded papers."""

    assistant = ctx.obj['assistant']

    try:
        papers = assistant.list_papers()

        if not papers:
            click.echo("📚 No papers uploaded yet")
            return

        click.echo(f"📚 Uploaded Papers ({len(papers)}):")
        click.echo("=" * 50)

        for paper in papers:
            click.echo(f"📄 {paper['title']}")
            click.echo(f"   ID: {paper['id']}")
            click.echo(f"   Authors: {', '.join(paper.get('authors', []))}")
            click.echo(f"   Pages: {paper.get('pages', 'N/A')}")
            click.echo()

    except Exception as e:
        click.echo(f"❌ Error listing papers: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--pattern', default='*.pdf', help='File pattern to match')
@click.option('--analyze', is_flag=True, help='Run analysis on all papers')
@click.option('--output-dir', type=click.Path(), help='Directory to save results')
@click.pass_context
def batch(ctx, directory, pattern, analyze, output_dir):
    """Batch process multiple papers in a directory."""

    assistant = ctx.obj['assistant']

    # Find all PDF files
    pdf_files = list(Path(directory).glob(pattern))

    if not pdf_files:
        click.echo(f"📁 No files found matching pattern: {pattern}")
        return

    click.echo(f"📁 Found {len(pdf_files)} files to process")

    if output_dir:
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    for pdf_file in pdf_files:
        click.echo(f"📄 Processing: {pdf_file.name}")

        try:
            # Upload paper
            paper_id = assistant.upload_paper(str(pdf_file))
            click.echo(f"✅ Uploaded: {paper_id}")

            if analyze:
                # Run analysis
                contribution = assistant.analyze_contribution(paper_id)
                summary = assistant.summarize_paper(paper_id)

                if output_dir:
                    # Save results
                    result_file = Path(output_dir) / \
                        f"{pdf_file.stem}_analysis.json"
                    with open(result_file, 'w') as f:
                        json.dump({
                            'paper_id': paper_id,
                            'filename': pdf_file.name,
                            'contribution': contribution,
                            'summary': summary
                        }, f, indent=2)
                    click.echo(f"📝 Analysis saved: {result_file}")

        except Exception as e:
            click.echo(f"❌ Error processing {pdf_file.name}: {e}")


if __name__ == '__main__':
    cli()
