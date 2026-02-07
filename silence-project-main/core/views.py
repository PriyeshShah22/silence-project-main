from django.shortcuts import render, redirect
from .forms import AnalysisForm
from .utils import process_data
from .ingestion import ingest_csv_to_db
from .ai_client import generate_insights
from .prompts import build_insights_prompt

# --- 1. STATIC PAGES ---
def index_view(request):
    return render(request, 'core/index.html')

def about_view(request):
    return render(request, 'core/about.html')

def working_view(request):
    return render(request, 'core/working.html')

def guide_view(request):
    """Renders the step-by-step user guide."""
    return render(request, 'core/guide.html')

# --- 2. LOGIC PAGES ---
def upload_view(request):
    """
    Handles CSV ingestion, statistical analysis, and AI insight generation.
    Returns the results to the integrated 'analysis.html' dashboard.
    """
    results = None

    if request.method == 'POST':
        form = AnalysisForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                dataset_file = request.FILES['dataset']
                # Get threshold from form or default to 0.5 (Mean * 0.5)
                threshold = form.cleaned_data.get('silence_threshold') or 0.5

                # 1) Persist to DB using the Admin-centric DBMS approach
                dataset = ingest_csv_to_db(dataset_file, threshold)

                # IMPORTANT: Reset file pointer for pandas after DB ingestion
                dataset_file.seek(0)

                # 2) Trigger analytics pipeline (chart/stats/ranking)
                # Pass the threshold to utils.py for Z-score and Fear Score calculation
                results = process_data(dataset_file, threshold)

                # 3) Build summary for the AI client
                summary = {
                    "columns_expected": ["region", "district", "population", "complaints", "history_avg"],
                    "threshold": float(threshold),
                    "computed_stats": results.get("stats", {}),
                    "flagged_preview": results.get("ranked_regions", [])[:10],
                    "row_count": len(results.get("full_data", [])),
                }

                # 4) Generate AI insights for the 'System Intelligence' section
                prompt = build_insights_prompt(summary)
                ai_text = generate_insights(prompt)

                # Append metadata to results for the template
                results["ai_insights"] = ai_text
                results["dataset_id"] = dataset.id

            except Exception as e:
                # Log errors for debugging while keeping the UI clean
                print(f"❌ Processing Error: {e}")
        else:
            print(f"❌ Form Error: {form.errors}")
    else:
        # Standard GET request returns the empty upload form
        form = AnalysisForm()

    # Note: Template path must match where your HTML file is stored
    return render(request, 'core/upload.html', {'form': form, 'results': results})

def results_view(request):
    """
    Redirects to the upload page since the unified dashboard 
    now handles results post-upload.
    """
    return redirect('upload')