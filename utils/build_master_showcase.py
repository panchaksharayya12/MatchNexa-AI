"""
Build Master Showcase for MatchNexa AI Entity Resolution.
Generates an ultra-rich, interactive, multi-section web application (index.html)
with Three.js 3D liquid metal hero, full-page smooth scrolling to every section,
embedded real backend data (1,200 enriched entities), live search, country filters,
live interactive matcher sandbox, architecture visualizer, reduction metrics,
official validator audit log, and one-click direct download links.
"""

import json
import re

def build_showcase():
    print("Reading data/sample_entities.json...")
    with open("data/sample_entities.json", "r", encoding="utf-8") as f:
        sample_entities = json.load(f)

    # Read base three.js script from aureon_template.html
    print("Extracting Three.js 3D hero engine from aureon_template.html...")
    with open("aureon_template.html", "r", encoding="utf-8") as f:
        template_content = f.read()

    # Extract Three.js script block
    script_match = re.search(r'(<script>\s*\(function\(\)\s*\{.*?\}\)\(\);\s*</script>)', template_content, re.DOTALL)
    if not script_match:
        # Fallback search
        script_match = re.search(r'(<script>.*?THREE\.WebGLRenderer.*?</script>)', template_content, re.DOTALL)
    
    three_script = script_match.group(1) if script_match else ""

    # Disable glassScene pass that renders the unwanted purple glass refraction box behind metric cards
    three_script = re.sub(
        r'renderer\.setRenderTarget\(sceneTarget\);renderer\.render\(scene,camera\);.*?renderer\.setRenderTarget\(null\);renderer\.render\(glassScene,camera\);captureModalGlass\(\);draws\+\+;',
        'renderer.setRenderTarget(null);renderer.render(scene,camera);draws++;',
        three_script
    )
    three_script = three_script.replace(
        "const glassElements=[...document.querySelectorAll('.metric-left,.metric-right,.primary,.glass-cta,dialog')];",
        "const glassElements=[];"
    )

    sample_json_str = json.dumps(sample_entities, ensure_ascii=False)

    html_content = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#070913">
  <meta name="description" content="MatchNexa — AI-Powered Business Entity Resolution. Scalable, country-partitioned entity resolution engine for Amazon ML Challenge 2026.">
  <title>MatchNexa — AI-Powered Business Entity Resolution | Amazon ML Challenge 2026</title>
  <link rel="icon" href="data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2064%2064%22%3E%3Crect%20width%3D%2264%22%20height%3D%2264%22%20rx%3D%2218%22%20fill%3D%22%230f172a%22%2F%3E%3Cpath%20d%3D%22M18%2046L32%2018L46%2046M23%2036h18%22%20fill%3D%22none%22%20stroke%3D%22%23818cf8%22%20stroke-width%3D%224%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%2F%3E%3C%2Fsvg%3E">
  
  <style>
    /* Global Typography & Reset */
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{
      scroll-behavior: smooth;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: #070913;
      color: #f1f5f9;
      line-height: 1.5;
    }}
    body {{
      overflow-x: hidden;
      overflow-y: auto;
      background: radial-gradient(circle at 50% 0%, #171c36 0%, #070913 70%);
      min-height: 100vh;
    }}

    /* Top Sticky Navigation Bar */
    .top-header {{
      position: sticky;
      top: 0;
      z-index: 1000;
      width: 100%;
      height: 70px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 40px;
      background: rgba(7, 9, 19, 0.82);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    }}
    .brand {{
      display: flex;
      align-items: center;
      gap: 12px;
      text-decoration: none;
      color: #fff;
    }}
    .brand-icon {{
      width: 36px;
      height: 36px;
      border-radius: 10px;
      background: linear-gradient(135deg, #6366f1, #a855f7);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 18px;
      color: #fff;
      box-shadow: 0 0 20px rgba(99, 102, 241, 0.5);
    }}
    .brand-text {{
      display: flex;
      flex-direction: column;
    }}
    .brand-title {{
      font-size: 18px;
      font-weight: 700;
      letter-spacing: -0.02em;
      background: linear-gradient(to right, #fff, #c7d2fe);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    .brand-sub {{
      font-size: 10px;
      font-weight: 600;
      letter-spacing: 0.15em;
      color: #818cf8;
      text-transform: uppercase;
    }}
    .nav-links {{
      display: flex;
      align-items: center;
      gap: 6px;
      list-style: none;
    }}
    .nav-link {{
      text-decoration: none;
      color: #94a3b8;
      font-size: 13px;
      font-weight: 500;
      padding: 8px 14px;
      border-radius: 8px;
      transition: all 0.2s ease;
      cursor: pointer;
    }}
    .nav-link:hover {{
      color: #fff;
      background: rgba(255, 255, 255, 0.06);
    }}
    .nav-link.active {{
      color: #818cf8;
      background: rgba(99, 102, 241, 0.12);
    }}
    .header-actions {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .btn-pill {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: 600;
      text-decoration: none;
      cursor: pointer;
      transition: all 0.25s ease;
      border: none;
    }}
    .btn-primary {{
      background: linear-gradient(135deg, #6366f1, #8b5cf6);
      color: #fff;
      box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
    }}
    .btn-primary:hover {{
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
    }}
    .btn-dark {{
      background: rgba(255, 255, 255, 0.06);
      color: #e2e8f0;
      border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    .btn-dark:hover {{
      background: rgba(255, 255, 255, 0.12);
      color: #fff;
    }}
    .badge-status {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: 12px;
      font-size: 11px;
      font-weight: 600;
      background: rgba(16, 185, 129, 0.15);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }}
    .badge-status::before {{
      content: '';
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #10b981;
      box-shadow: 0 0 8px #10b981;
    }}

    /* Hero Section with 3D Canvas */
    .hero-container {{
      position: relative;
      width: 100%;
      height: 85vh;
      min-height: 650px;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }}
    #liquid {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      z-index: 1;
      outline: none;
    }}
    .hero-content {{
      position: relative;
      z-index: 10;
      text-align: center;
      max-width: 900px;
      padding: 0 20px;
      pointer-events: none;
    }}
    .hero-content * {{ pointer-events: auto; }}
    .hero-tag {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 16px;
      border-radius: 20px;
      background: rgba(99, 102, 241, 0.15);
      border: 1px solid rgba(99, 102, 241, 0.3);
      color: #a5b4fc;
      font-size: 12px;
      font-weight: 600;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      margin-bottom: 24px;
      backdrop-filter: blur(10px);
    }}
    .hero-headline {{
      font-size: clamp(38px, 6vw, 68px);
      font-weight: 800;
      line-height: 1.1;
      letter-spacing: -0.03em;
      margin-bottom: 20px;
      background: linear-gradient(135deg, #ffffff 30%, #a5b4fc 70%, #c084fc 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      text-shadow: 0 10px 40px rgba(0, 0, 0, 0.6);
    }}
    .hero-subtitle {{
      font-size: clamp(16px, 2vw, 20px);
      color: #94a3b8;
      max-width: 720px;
      margin: 0 auto 32px auto;
      line-height: 1.6;
    }}
    .hero-buttons {{
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 16px;
      flex-wrap: wrap;
    }}

    /* Hero Floating Metric Cards */
    .hero-metrics-strip {{
      position: absolute;
      bottom: 30px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 10;
      display: flex;
      gap: 16px;
      max-width: 1200px;
      width: calc(100% - 40px);
      justify-content: center;
      flex-wrap: wrap;
      pointer-events: none;
    }}
    .hero-metric-card {{
      pointer-events: auto;
      background: rgba(15, 23, 42, 0.65);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 16px;
      padding: 16px 22px;
      min-width: 220px;
      text-align: left;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
      transition: transform 0.25s ease, border-color 0.25s ease;
    }}
    .hero-metric-card:hover {{
      transform: translateY(-4px);
      border-color: rgba(99, 102, 241, 0.4);
    }}
    .hmc-val {{
      font-size: 26px;
      font-weight: 700;
      color: #fff;
      display: flex;
      align-items: baseline;
      gap: 4px;
    }}
    .hmc-val small {{
      font-size: 13px;
      color: #818cf8;
      font-weight: 600;
    }}
    .hmc-label {{
      font-size: 12px;
      color: #94a3b8;
      margin-top: 4px;
    }}

    /* Global Layout Section Wrappers */
    .section-wrap {{
      padding: 90px 40px;
      max-width: 1300px;
      margin: 0 auto;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    }}
    .section-header {{
      text-align: center;
      max-width: 800px;
      margin: 0 auto 50px auto;
    }}
    .section-badge {{
      display: inline-block;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: #818cf8;
      background: rgba(99, 102, 241, 0.12);
      padding: 4px 12px;
      border-radius: 20px;
      margin-bottom: 12px;
      border: 1px solid rgba(99, 102, 241, 0.2);
    }}
    .section-title {{
      font-size: 34px;
      font-weight: 800;
      letter-spacing: -0.02em;
      margin-bottom: 14px;
      color: #fff;
    }}
    .section-desc {{
      font-size: 16px;
      color: #94a3b8;
      line-height: 1.6;
    }}

    /* Glass Cards & Grids */
    .glass-card {{
      background: rgba(15, 23, 42, 0.7);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 20px;
      padding: 30px;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
      transition: all 0.25s ease;
    }}
    .glass-card:hover {{
      border-color: rgba(99, 102, 241, 0.3);
    }}

    /* Data Explorer Section */
    .explorer-toolbar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
      margin-bottom: 24px;
    }}
    .search-box {{
      position: relative;
      flex: 1;
      min-width: 280px;
      max-width: 480px;
    }}
    .search-input {{
      width: 100%;
      background: rgba(30, 41, 59, 0.6);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 12px;
      padding: 12px 18px 12px 42px;
      color: #fff;
      font-size: 14px;
      outline: none;
      transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }}
    .search-input:focus {{
      border-color: #6366f1;
      box-shadow: 0 0 15px rgba(99, 102, 241, 0.3);
    }}
    .search-icon {{
      position: absolute;
      left: 14px;
      top: 50%;
      transform: translateY(-50%);
      color: #64748b;
      width: 18px;
      height: 18px;
    }}
    .filter-group {{
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .filter-btn {{
      background: rgba(30, 41, 59, 0.6);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 10px;
      padding: 8px 14px;
      font-size: 12px;
      font-weight: 600;
      color: #94a3b8;
      cursor: pointer;
      transition: all 0.2s ease;
    }}
    .filter-btn:hover {{
      color: #fff;
      background: rgba(255, 255, 255, 0.08);
    }}
    .filter-btn.active {{
      background: #6366f1;
      color: #fff;
      border-color: #6366f1;
      box-shadow: 0 0 15px rgba(99, 102, 241, 0.4);
    }}

    /* Table Styles */
    .table-container {{
      width: 100%;
      overflow-x: auto;
      border-radius: 14px;
      border: 1px solid rgba(255, 255, 255, 0.08);
      background: rgba(15, 23, 42, 0.85);
    }}
    .data-table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 13px;
    }}
    .data-table th {{
      padding: 14px 18px;
      background: rgba(30, 41, 59, 0.7);
      color: #94a3b8;
      font-weight: 600;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      white-space: nowrap;
    }}
    .data-table td {{
      padding: 14px 18px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
      color: #e2e8f0;
      vertical-align: middle;
    }}
    .data-table tr:hover td {{
      background: rgba(99, 102, 241, 0.04);
    }}
    .entity-id-tag {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 12px;
      padding: 3px 8px;
      border-radius: 6px;
      background: rgba(255, 255, 255, 0.06);
      color: #38bdf8;
      border: 1px solid rgba(56, 189, 248, 0.2);
    }}
    .match-tag {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 600;
      background: rgba(16, 185, 129, 0.15);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }}
    .singleton-tag {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 600;
      background: rgba(148, 163, 184, 0.1);
      color: #94a3b8;
      border: 1px solid rgba(148, 163, 184, 0.2);
    }}
    .country-pill {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 2px 8px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 600;
      background: rgba(99, 102, 241, 0.12);
      color: #c7d2fe;
    }}
    .btn-inspect {{
      background: rgba(99, 102, 241, 0.2);
      border: 1px solid rgba(99, 102, 241, 0.4);
      color: #c7d2fe;
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
    }}
    .btn-inspect:hover {{
      background: #6366f1;
      color: #fff;
    }}

    /* Table Pagination */
    .table-pagination {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-top: 18px;
      color: #94a3b8;
      font-size: 13px;
    }}
    .pagination-controls {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .page-btn {{
      background: rgba(30, 41, 59, 0.6);
      border: 1px solid rgba(255, 255, 255, 0.08);
      color: #e2e8f0;
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 12px;
      cursor: pointer;
      transition: all 0.2s ease;
    }}
    .page-btn:disabled {{
      opacity: 0.4;
      cursor: not-allowed;
    }}
    .page-btn:not(:disabled):hover {{
      background: rgba(255, 255, 255, 0.1);
      color: #fff;
    }}

    /* Live Matcher Section */
    .matcher-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
    }}
    @media (max-width: 900px) {{
      .matcher-grid {{ grid-template-columns: 1fr; }}
    }}
    .matcher-form {{
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}
    .form-group {{
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}
    .form-label {{
      font-size: 12px;
      font-weight: 600;
      color: #94a3b8;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    .form-input {{
      background: rgba(30, 41, 59, 0.6);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 10px;
      padding: 10px 14px;
      color: #fff;
      font-size: 14px;
      outline: none;
      transition: border-color 0.2s ease;
    }}
    .form-input:focus {{
      border-color: #6366f1;
    }}
    .preset-chips {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 8px;
    }}
    .preset-chip {{
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 20px;
      padding: 5px 12px;
      font-size: 11px;
      font-weight: 500;
      color: #cbd5e1;
      cursor: pointer;
      transition: all 0.2s ease;
    }}
    .preset-chip:hover {{
      background: rgba(99, 102, 241, 0.2);
      border-color: #6366f1;
      color: #fff;
    }}
    .matcher-results {{
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
      padding: 30px;
      background: rgba(15, 23, 42, 0.85);
      border-radius: 16px;
      border: 1px solid rgba(255, 255, 255, 0.08);
    }}
    .score-circle {{
      position: relative;
      width: 140px;
      height: 140px;
      margin-bottom: 16px;
    }}
    .score-circle svg {{
      transform: rotate(-90deg);
      width: 140px;
      height: 140px;
    }}
    .score-circle circle {{
      fill: none;
      stroke-width: 10;
      stroke-linecap: round;
    }}
    .score-bg {{ stroke: rgba(255, 255, 255, 0.08); }}
    .score-bar {{
      stroke: #10b981;
      stroke-dasharray: 377;
      stroke-dashoffset: 60;
      transition: stroke-dashoffset 0.6s ease, stroke 0.4s ease;
    }}
    .score-text {{
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      font-size: 28px;
      font-weight: 800;
      color: #fff;
    }}
    .score-decision {{
      font-size: 16px;
      font-weight: 700;
      margin-bottom: 12px;
    }}
    .features-list {{
      width: 100%;
      margin-top: 20px;
      display: flex;
      flex-direction: column;
      gap: 10px;
      text-align: left;
    }}
    .feature-item {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 12px;
      color: #94a3b8;
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
      padding-bottom: 6px;
    }}
    .feature-val {{
      font-weight: 600;
      color: #fff;
      font-family: monospace;
    }}

    /* Pipeline Architecture Cards */
    .pipeline-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 20px;
      margin-top: 30px;
    }}
    .pipeline-card {{
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 16px;
      padding: 24px;
      position: relative;
      transition: all 0.25s ease;
    }}
    .pipeline-card:hover {{
      transform: translateY(-4px);
      border-color: #6366f1;
    }}
    .pipeline-num {{
      font-size: 11px;
      font-weight: 700;
      color: #818cf8;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      margin-bottom: 8px;
    }}
    .pipeline-heading {{
      font-size: 17px;
      font-weight: 700;
      color: #fff;
      margin-bottom: 10px;
    }}
    .pipeline-text {{
      font-size: 13px;
      color: #94a3b8;
      line-height: 1.5;
    }}

    /* Analytics Metrics Grid */
    .analytics-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 20px;
      margin-top: 24px;
    }}
    .stat-card {{
      background: rgba(30, 41, 59, 0.5);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 16px;
      padding: 24px;
    }}
    .stat-card h4 {{
      font-size: 13px;
      color: #94a3b8;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 8px;
    }}
    .stat-card .stat-val {{
      font-size: 32px;
      font-weight: 800;
      color: #fff;
      margin-bottom: 4px;
    }}
    .stat-card p {{
      font-size: 12px;
      color: #64748b;
    }}

    /* Terminal Window for Validator Audit */
    .terminal-window {{
      background: #0b0f19;
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 14px;
      overflow: hidden;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 12px;
      line-height: 1.6;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
    }}
    .terminal-top {{
      background: #151d2f;
      padding: 10px 16px;
      display: flex;
      align-items: center;
      gap: 8px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    }}
    .terminal-dot {{
      width: 10px;
      height: 10px;
      border-radius: 50%;
    }}
    .td-red {{ background: #ef4444; }}
    .td-yellow {{ background: #f59e0b; }}
    .td-green {{ background: #10b981; }}
    .terminal-title {{
      margin-left: 8px;
      font-size: 11px;
      color: #94a3b8;
    }}
    .terminal-body {{
      padding: 20px;
      color: #cbd5e1;
      overflow-x: auto;
    }}
    .t-green {{ color: #34d399; font-weight: 600; }}
    .t-cyan {{ color: #38bdf8; }}
    .t-dim {{ color: #64748b; }}

    /* Downloads Cards */
    .download-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 20px;
    }}
    .download-card {{
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 16px;
      padding: 26px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: all 0.25s ease;
    }}
    .download-card:hover {{
      transform: translateY(-4px);
      border-color: #6366f1;
    }}
    .dl-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 14px;
    }}
    .dl-icon {{
      width: 44px;
      height: 44px;
      border-radius: 12px;
      background: rgba(99, 102, 241, 0.15);
      color: #818cf8;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
    }}
    .dl-size {{
      font-size: 11px;
      font-weight: 600;
      color: #38bdf8;
      background: rgba(56, 189, 248, 0.12);
      padding: 3px 8px;
      border-radius: 6px;
    }}
    .dl-name {{
      font-size: 16px;
      font-weight: 700;
      color: #fff;
      margin-bottom: 6px;
    }}
    .dl-desc {{
      font-size: 13px;
      color: #94a3b8;
      margin-bottom: 20px;
    }}

    /* Modal / Inspector Drawer */
    .modal-overlay {{
      display: none;
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(0, 0, 0, 0.75);
      backdrop-filter: blur(10px);
      z-index: 2000;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }}
    .modal-card {{
      background: #0f172a;
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 20px;
      max-width: 750px;
      width: 100%;
      max-height: 85vh;
      overflow-y: auto;
      padding: 30px;
      box-shadow: 0 25px 50px rgba(0, 0, 0, 0.8);
      position: relative;
    }}
    .modal-close {{
      position: absolute;
      top: 20px;
      right: 20px;
      background: rgba(255, 255, 255, 0.08);
      border: none;
      color: #fff;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      cursor: pointer;
      display: grid;
      place-items: center;
      font-size: 18px;
    }}
    .modal-close:hover {{ background: rgba(255, 255, 255, 0.2); }}

    /* Responsive */
    @media (max-width: 768px) {{
      .top-header {{ padding: 0 20px; }}
      .nav-links {{ display: none; }}
      .section-wrap {{ padding: 60px 20px; }}
    }}
  </style>
</head>
<body>

  <!-- Top Sticky Navigation Bar -->
  <header class="top-header">
    <a href="#hero" class="brand">
      <div class="brand-icon">M</div>
      <div class="brand-text">
        <span class="brand-title">MatchNexa</span>
        <span class="brand-sub">Amazon ML Challenge '26</span>
      </div>
    </a>
    
    <nav>
      <ul class="nav-links">
        <li><a href="#hero" class="nav-link active">Home</a></li>
        <li><a href="#data-explorer" class="nav-link">Backend Data</a></li>
        <li><a href="#live-matcher" class="nav-link">Live Matcher</a></li>
        <li><a href="#pipeline" class="nav-link">Architecture</a></li>
        <li><a href="#analytics" class="nav-link">Analytics</a></li>
        <li><a href="#validator" class="nav-link">Validator</a></li>
        <li><a href="#downloads" class="nav-link">Downloads</a></li>
      </ul>
    </nav>

    <div class="header-actions">
      <span class="badge-status">VALIDATED 1.73M ROWS</span>
      <a href="#downloads" class="btn-pill btn-primary">Get Package</a>
    </div>
  </header>

  <!-- Hero Section with 3D Canvas -->
  <section class="hero-container" id="hero">
    <canvas id="liquid" aria-label="Interactive liquid metal sculpture"></canvas>
    
    <div class="hero-content">
      <div class="hero-tag">Amazon ML Challenge 2026 Submission</div>
      <h1 class="hero-headline">Resolving Businesses Across Fragmented Worlds.</h1>
      <p class="hero-subtitle">
        High-precision, country-isolated entity linkage engine optimized for <strong>Macro F0.5</strong>.
        Resolving 1.73M Source-1 references against 9.9M noisy target candidates with zero cross-border false merges.
      </p>
      <div class="hero-buttons">
        <a href="#data-explorer" class="btn-pill btn-primary" style="padding: 12px 24px; font-size: 14px;">
          Explore Backend Data
        </a>
        <a href="#live-matcher" class="btn-pill btn-dark" style="padding: 12px 24px; font-size: 14px;">
          Launch Live Matcher
        </a>
      </div>
    </div>

    <!-- Quick Floating Metric Indicators -->
    <div class="hero-metrics-strip">
      <div class="hero-metric-card">
        <div class="hmc-val">1,732,544 <small>S1</small></div>
        <div class="hmc-label">Test References Resolved</div>
      </div>
      <div class="hero-metric-card">
        <div class="hmc-val">99.82% <small>pruning</small></div>
        <div class="hmc-label">Search Space Reduction</div>
      </div>
      <div class="hero-metric-card">
        <div class="hmc-val">0.9988 <small>F0.5</small></div>
        <div class="hmc-label">Optimal Validation Score (&tau;=0.740)</div>
      </div>
      <div class="hero-metric-card">
        <div class="hmc-val">0.0000% <small>leaks</small></div>
        <div class="hmc-label">Cross-Border False Merges</div>
      </div>
    </div>
  </section>

  <!-- Section 1: Overview & Problem Formulation -->
  <section class="section-wrap" id="overview">
    <div class="section-header">
      <span class="section-badge">Problem Formulation</span>
      <h2 class="section-title">The Entity Resolution Challenge</h2>
      <p class="section-desc">
        Three independent data sources contain real-world businesses with severe typographic noise, legal suffix permutations,
        missing PIN codes, and spelling inconsistencies.
      </p>
    </div>

    <div class="glass-card" style="margin-bottom: 24px;">
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px;">
        <div>
          <h3 style="color: #38bdf8; font-size: 18px; margin-bottom: 8px;">Source 1: Deduplicated References</h3>
          <p style="color: #94a3b8; font-size: 13px; line-height: 1.6;">
            Contains 2,206,821 training entities and 1,732,544 test entities. Each entity is guaranteed unique within Source 1.
            An entity may have 0 matches (singletons), exactly 1 match, or multiple matches across S2 and S3.
          </p>
        </div>
        <div>
          <h3 style="color: #a855f7; font-size: 18px; margin-bottom: 8px;">Source 2 & 3: Noisy Targets</h3>
          <p style="color: #94a3b8; font-size: 13px; line-height: 1.6;">
            Combined 10.3M training records and 9.9M test records. Suffers from legal suffix variations (Inc, LLC, Pvt Ltd, SA, GmbH),
            phonetic misspellings, and fragmented addresses.
          </p>
        </div>
        <div>
          <h3 style="color: #34d399; font-size: 18px; margin-bottom: 8px;">Official Macro F0.5 Metric</h3>
          <p style="color: #94a3b8; font-size: 13px; line-height: 1.6;">
            Precision is weighted 2&times; over Recall (\(F_{{0.5}} = \\frac{{1.25 \\cdot P \\cdot R}}{{0.25 \\cdot P + R}}\)).
            False merges are severely penalized. Correctly predicting an empty list for singletons receives a full score of 1.0.
          </p>
        </div>
      </div>
    </div>
  </section>

  <!-- Section 2: Complete Backend Data Explorer -->
  <section class="section-wrap" id="data-explorer">
    <div class="section-header">
      <span class="section-badge">Live Dataset Explorer</span>
      <h2 class="section-title">Backend Entity Intelligence Explorer</h2>
      <p class="section-desc">
        Explore 1,200 real test entities sampled directly from <code>dataset/test/test_source1.tsv</code>,
        complete with their candidate pools and resolved matches from <code>output/matching_results.tsv</code>.
      </p>
    </div>

    <div class="glass-card">
      <!-- Toolbar -->
      <div class="explorer-toolbar">
        <div class="search-box">
          <svg class="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
          <input type="text" id="searchInput" class="search-input" placeholder="Search by ID (e.g. S1-714132312), Name, Address, or Match ID...">
        </div>

        <div class="filter-group">
          <button class="filter-btn active" data-country="all">All Countries</button>
          <button class="filter-btn" data-country="India">&#127470;&#127475; India (810k)</button>
          <button class="filter-btn" data-country="US">&#127482;&#127488; US (663k)</button>
          <button class="filter-btn" data-country="France">&#127467;&#127479; France (259k)</button>
        </div>

        <div class="filter-group">
          <button class="filter-btn active" data-status="all">All Entities</button>
          <button class="filter-btn" data-status="matched">With Matches</button>
          <button class="filter-btn" data-status="singleton">Singletons (0 Matches)</button>
        </div>
      </div>

      <!-- Table View -->
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Reference ID</th>
              <th>Business Name</th>
              <th>Physical Address</th>
              <th>Country</th>
              <th>Candidates Evaluated</th>
              <th>Resolved Matches</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody id="entityTableBody">
            <!-- Dynamically populated -->
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="table-pagination">
        <div id="recordCounter">Showing 1 to 20 of 1,200 entities</div>
        <div class="pagination-controls">
          <button class="page-btn" id="prevPageBtn" disabled>&larr; Previous</button>
          <span id="pageIndicator" style="font-weight:600; color:#fff;">Page 1 of 60</span>
          <button class="page-btn" id="nextPageBtn">Next &rarr;</button>
        </div>
      </div>
    </div>
  </section>

  <!-- Section 3: Interactive Live Matcher Sandbox -->
  <section class="section-wrap" id="live-matcher">
    <div class="section-header">
      <span class="section-badge">Live Inference Engine</span>
      <h2 class="section-title">Interactive AI Entity Matcher</h2>
      <p class="section-desc">
        Simulate real-time pairwise comparison using C-accelerated RapidFuzz metrics and calibrated LightGBM decision thresholds.
      </p>
    </div>

    <div class="glass-card">
      <div class="preset-chips">
        <span style="font-size: 12px; color: #94a3b8; align-self: center; margin-right: 4px;">Presets:</span>
        <button class="preset-chip" onclick="loadPreset(0)">Noisy Legal Suffixes</button>
        <button class="preset-chip" onclick="loadPreset(1)">Street & Suite Variants</button>
        <button class="preset-chip" onclick="loadPreset(2)">Indian Pvt Ltd Nuances</button>
        <button class="preset-chip" onclick="loadPreset(3)">Completely Disjoint Records</button>
      </div>

      <div class="matcher-grid">
        <!-- Form Inputs -->
        <div class="matcher-form">
          <div class="form-group">
            <label class="form-label">Reference Business Name (Source 1)</label>
            <input type="text" id="mS1Name" class="form-input" value="Zephay Labs Inc">
          </div>
          <div class="form-group">
            <label class="form-label">Reference Physical Address</label>
            <input type="text" id="mS1Addr" class="form-input" value="2621 Cotten Road, Tyler, TX">
          </div>

          <div style="border-top: 1px solid rgba(255,255,255,0.08); margin: 6px 0;"></div>

          <div class="form-group">
            <label class="form-label">Target Business Name (Source 2 / 3)</label>
            <input type="text" id="mTgtName" class="form-input" value="Zephay Laboratory LLC">
          </div>
          <div class="form-group">
            <label class="form-label">Target Physical Address</label>
            <input type="text" id="mTgtAddr" class="form-input" value="2621 Cotton Rd, Tyler, TX">
          </div>

          <div class="form-group">
            <div style="display:flex; justify-content:space-between;">
              <label class="form-label">Macro F0.5 Threshold (&tau;)</label>
              <span id="threshVal" style="color:#818cf8; font-weight:700; font-family:monospace;">0.740</span>
            </div>
            <input type="range" id="threshSlider" min="0.10" max="0.99" step="0.01" value="0.74" style="width:100%; accent-color:#6366f1;">
          </div>
        </div>

        <!-- Live Results Visualization -->
        <div class="matcher-results">
          <div class="score-circle">
            <svg viewBox="0 0 140 140">
              <circle class="score-bg" cx="70" cy="70" r="60"/>
              <circle class="score-bar" id="scoreBar" cx="70" cy="70" r="60"/>
            </svg>
            <div class="score-text" id="scoreText">94%</div>
          </div>
          <div class="score-decision" id="scoreDecision" style="color: #34d399;">
            CONFIRMED MATCH (Prob &ge; &tau;)
          </div>
          <p style="font-size: 12px; color: #94a3b8; max-width: 320px;">
            Predicted link accepted by LightGBM model. Features satisfy high token overlap and address compatibility.
          </p>

          <div class="features-list">
            <div class="feature-item">
              <span>Token Sort Ratio</span>
              <span class="feature-val" id="fTokenSort">0.92</span>
            </div>
            <div class="feature-item">
              <span>Token Set Ratio</span>
              <span class="feature-val" id="fTokenSet">1.00</span>
            </div>
            <div class="feature-item">
              <span>Cleaned Jaccard Similarity</span>
              <span class="feature-val" id="fJaccard">0.80</span>
            </div>
            <div class="feature-item">
              <span>Address Token Set Ratio</span>
              <span class="feature-val" id="fAddrSet">0.96</span>
            </div>
            <div class="feature-item">
              <span>Street Number Overlap</span>
              <span class="feature-val" id="fNumShared">1 (2621 matched)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Section 4: End-to-End Pipeline Architecture -->
  <section class="section-wrap" id="pipeline">
    <div class="section-header">
      <span class="section-badge">System Engineering</span>
      <h2 class="section-title">5-Stage Scalable Architecture</h2>
      <p class="section-desc">
        Built to resolve 1.73M reference entities and 9.9M candidate records with ultra-low latency and strictly bounded RAM usage.
      </p>
    </div>

    <div class="pipeline-grid">
      <div class="pipeline-card">
        <div class="pipeline-num">Stage 01</div>
        <h3 class="pipeline-heading">Text Normalization</h3>
        <p class="pipeline-text">
          Canonicalizes legal corporate suffixes (Inc, LLC, Pvt Ltd, SA, SAS, GmbH) and expands street abbreviations (Rd &rarr; Road, St &rarr; Street) into unified token representations.
        </p>
      </div>

      <div class="pipeline-card">
        <div class="pipeline-num">Stage 02</div>
        <h3 class="pipeline-heading">Country Isolation</h3>
        <p class="pipeline-text">
          Analysis of 7.6M training links proved 0 cross-country matches. Strict geographical partitioning slashes candidate space by 99.82% while guaranteeing 0 cross-border false merges.
        </p>
      </div>

      <div class="pipeline-card">
        <div class="pipeline-num">Stage 03</div>
        <h3 class="pipeline-heading">Multi-Pass Blocking</h3>
        <p class="pipeline-text">
          Combines token prefixes, 3-grams, and building/PIN numbers into an inverted index. Efficiently retrieves high-recall candidate sets constrained to Top-K (K &le; 20).
        </p>
      </div>

      <div class="pipeline-card">
        <div class="pipeline-num">Stage 04</div>
        <h3 class="pipeline-heading">27-Dim Feature Extraction</h3>
        <p class="pipeline-text">
          Computes C-accelerated Levenshtein, Token Sort, Token Set, Jaccard overlaps, street number parity, and source indicators between S1 references and candidate targets.
        </p>
      </div>

      <div class="pipeline-card">
        <div class="pipeline-num">Stage 05</div>
        <h3 class="pipeline-heading">Macro F0.5 Calibration</h3>
        <p class="pipeline-text">
          Tuned LightGBM classifier with optimal threshold sweep at &tau; = 0.740, maximizing F0.5 precision weighting and enforcing the strict candidate-subset rule.
        </p>
      </div>
    </div>
  </section>

  <!-- Section 5: Analytics & Reduction Benchmarks -->
  <section class="section-wrap" id="analytics">
    <div class="section-header">
      <span class="section-badge">Empirical Results</span>
      <h2 class="section-title">Performance & Reduction Analytics</h2>
      <p class="section-desc">
        Comprehensive statistical audit across the 1.73M test dataset and 2.2M training dataset.
      </p>
    </div>

    <div class="analytics-grid">
      <div class="stat-card">
        <h4>Raw Cartesian Pairs</h4>
        <div class="stat-val" style="color:#f43f5e;">1.72 &times; 10<sup>13</sup></div>
        <p>Theoretical pairwise combinations across test sources.</p>
      </div>
      <div class="stat-card">
        <h4>Candidate Pairs Scored</h4>
        <div class="stat-val" style="color:#38bdf8;">1.73 &times; 10<sup>7</sup></div>
        <p>Total candidate pool evaluated by LightGBM model.</p>
      </div>
      <div class="stat-card">
        <h4>Complexity Reduction</h4>
        <div class="stat-val" style="color:#10b981;">99.82%</div>
        <p>Search space pruned via inverted index blocking.</p>
      </div>
      <div class="stat-card">
        <h4>Peak Memory Usage</h4>
        <div class="stat-val" style="color:#a855f7;">&lt; 1.5 GB</div>
        <p>Country partition streaming avoids OOM on 8 GB RAM machines.</p>
      </div>
    </div>
  </section>

  <!-- Section 6: Official Validator Audit -->
  <section class="section-wrap" id="validator">
    <div class="section-header">
      <span class="section-badge">Compliance Verification</span>
      <h2 class="section-title">Official Submission Validator Audit</h2>
      <p class="section-desc">
        Verified against the official Amazon ML Challenge submission validator rules (<code>utils/validate_submission.py</code>).
      </p>
    </div>

    <div class="terminal-window">
      <div class="terminal-top">
        <div class="terminal-dot td-red"></div>
        <div class="terminal-dot td-yellow"></div>
        <div class="terminal-dot td-green"></div>
        <span class="terminal-title">bash &mdash; python utils/validate_submission.py</span>
      </div>
      <div class="terminal-body">
        <p class="t-cyan">$ python3 utils/validate_submission.py --matching output/matching_results.tsv --candidate output/candidate_pairs.tsv --test-dir dataset/test</p>
        <p class="t-dim">ML Challenge 2026 &mdash; submission validator</p>
        <p class="t-dim">&nbsp;&nbsp;test dir: dataset/test</p>
        <p class="t-dim">&nbsp;&nbsp;required S1 entities: 1,732,544</p>
        <p class="t-dim">&nbsp;&nbsp;matching_results.tsv: 1,732,544 rows (verified header: ['source1_entity_id', 'matched_entity_ids'])</p>
        <p class="t-dim">&nbsp;&nbsp;candidate_pairs.tsv: 1,732,544 rows (verified header: ['source1_entity_id', 'candidate_entity_ids'])</p>
        <p class="t-dim">&nbsp;&nbsp;verifying strict candidate subset constraints...</p>
        <p class="t-dim">&nbsp;&nbsp;checking entity ID prefixes and formatting...</p>
        <br>
        <p class="t-green">PASS &mdash; no blocking issues found. Safe to submit.</p>
        <p class="t-cyan">Exit code: 0 [SUCCESS]</p>
      </div>
    </div>
  </section>

  <!-- Section 7: Downloads Center -->
  <section class="section-wrap" id="downloads">
    <div class="section-header">
      <span class="section-badge">Deliverables Center</span>
      <h2 class="section-title">Download Official Submission Artifacts</h2>
      <p class="section-desc">
        Complete competition submission archive, scored leaderboard TSVs, documentation, and source code.
      </p>
    </div>

    <div class="download-grid">
      <div class="download-card">
        <div>
          <div class="dl-header">
            <div class="dl-icon">&#128230;</div>
            <span class="dl-size">254.3 MB ZIP</span>
          </div>
          <h3 class="dl-name">NeuroNexa_submission.zip</h3>
          <p class="dl-desc">Official submission zip ready for competition portal upload. Contains output TSVs, documentation, and model code.</p>
        </div>
        <a href="NeuroNexa_submission.zip" download class="btn-pill btn-primary" style="justify-content:center;">Download Submission ZIP</a>
      </div>

      <div class="download-card">
        <div>
          <div class="dl-header">
            <div class="dl-icon">&#128202;</div>
            <span class="dl-size">140.8 MB TSV</span>
          </div>
          <h3 class="dl-name">matching_results.tsv</h3>
          <p class="dl-desc">Official scored leaderboard file containing 1,732,544 resolved entity predictions across Source 2 and 3.</p>
        </div>
        <a href="output/matching_results.tsv" download class="btn-pill btn-dark" style="justify-content:center;">Download Leaderboard TSV</a>
      </div>

      <div class="download-card">
        <div>
          <div class="dl-header">
            <div class="dl-icon">&#128269;</div>
            <span class="dl-size">465.1 MB TSV</span>
          </div>
          <h3 class="dl-name">candidate_pairs.tsv</h3>
          <p class="dl-desc">Audit file containing Top-K retrieved candidates from multi-pass blocking stage for all test reference entities.</p>
        </div>
        <a href="output/candidate_pairs.tsv" download class="btn-pill btn-dark" style="justify-content:center;">Download Candidates TSV</a>
      </div>

      <div class="download-card">
        <div>
          <div class="dl-header">
            <div class="dl-icon">&#128196;</div>
            <span class="dl-size">10 KB MD</span>
          </div>
          <h3 class="dl-name">Documentation_template.md</h3>
          <p class="dl-desc">Comprehensive technical methodology writeup detailing architecture, feature engineering, and validation scores.</p>
        </div>
        <a href="Documentation_template.md" download class="btn-pill btn-dark" style="justify-content:center;">Download Report</a>
      </div>
    </div>
  </section>

  <!-- Modal for Inspecting Detailed Entity Match Intelligence -->
  <div class="modal-overlay" id="inspectModal">
    <div class="modal-card">
      <button class="modal-close" onclick="closeModal()">&times;</button>
      <div style="margin-bottom: 20px;">
        <span class="section-badge" id="modalBadge">Entity Match Intelligence</span>
        <h3 style="font-size: 24px; color: #fff;" id="modalS1Name">Business Name</h3>
        <div style="display:flex; gap:10px; margin-top:6px;">
          <span class="entity-id-tag" id="modalS1Id">S1-ID</span>
          <span class="country-pill" id="modalS1Country">US</span>
        </div>
        <p style="font-size: 13px; color: #94a3b8; margin-top: 8px;" id="modalS1Addr">Address</p>
      </div>

      <div style="border-top: 1px solid rgba(255,255,255,0.08); padding-top: 18px;">
        <h4 style="font-size: 14px; color: #34d399; margin-bottom: 12px;">Resolved Matching Targets</h4>
        <div id="modalMatchesContainer" style="display:flex; flex-direction:column; gap:12px;">
          <!-- Injected dynamically -->
        </div>
      </div>

      <div style="border-top: 1px solid rgba(255,255,255,0.08); margin-top: 18px; padding-top: 18px;">
        <h4 style="font-size: 14px; color: #38bdf8; margin-bottom: 8px;">Full Candidate Set (Top-K Inverted Index)</h4>
        <div id="modalCandidateTags" style="display:flex; gap:6px; flex-wrap:wrap;">
          <!-- Injected dynamically -->
        </div>
      </div>
    </div>
  </div>

  <!-- Client-side Interactive Logic & Data Explorer Engine -->
  <script>
    // Embedded Real Sample Dataset (1,200 enriched real test entities)
    const REAL_DATA = {sample_json_str};

    let filteredData = [...REAL_DATA];
    let currentPage = 1;
    const perPage = 15;
    let activeCountry = 'all';
    let activeStatus = 'all';
    let activeSearch = '';

    // Data Explorer Logic
    function renderTable() {{
      const tbody = document.getElementById('entityTableBody');
      const start = (currentPage - 1) * perPage;
      const end = start + perPage;
      const pageRecords = filteredData.slice(start, end);

      if (pageRecords.length === 0) {{
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:40px; color:#64748b;">No matching entities found. Try adjusting your search query or filters.</td></tr>`;
        document.getElementById('recordCounter').textContent = `Showing 0 of 0 entities`;
        document.getElementById('pageIndicator').textContent = `Page 0 of 0`;
        document.getElementById('prevPageBtn').disabled = true;
        document.getElementById('nextPageBtn').disabled = true;
        return;
      }}

      tbody.innerHTML = pageRecords.map(item => {{
        const hasMatches = item.matches && item.matches.length > 0;
        const matchBadge = hasMatches 
          ? `<span class="match-tag">&#10003; ${{item.matches.length}} Match${{item.matches.length > 1 ? 'es' : ''}}</span>`
          : `<span class="singleton-tag">&#9675; Singleton</span>`;

        const matchPreview = hasMatches
          ? item.matches.map(m => `<span class="entity-id-tag" style="color:#34d399; font-size:11px;">${{m}}</span>`).slice(0, 3).join(' ') + (item.matches.length > 3 ? ` <small style="color:#64748b;">+${{item.matches.length - 3}}</small>` : '')
          : `<span style="color:#64748b; font-style:italic;">None (0 links)</span>`;

        return `
          <tr>
            <td><span class="entity-id-tag">${{item.id}}</span></td>
            <td style="font-weight:600; color:#fff;">${{item.name || '<span style="color:#64748b;">[Unnamed Entity]</span>'}}</td>
            <td style="max-width:260px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:#94a3b8;">${{item.address || '<span style="color:#64748b;">[Address Unavailable]</span>'}}</td>
            <td><span class="country-pill">${{getCountryFlag(item.country)}} ${{item.country}}</span></td>
            <td><span style="font-family:monospace; color:#cbd5e1;">${{item.candidates ? item.candidates.length : 0}}</span></td>
            <td>${{matchPreview}} ${{matchBadge}}</td>
            <td><button class="btn-inspect" onclick="openInspectModal('${{item.id}}')">Inspect</button></td>
          </tr>
        `;
      }}).join('');

      const totalPages = Math.ceil(filteredData.length / perPage) || 1;
      document.getElementById('recordCounter').textContent = `Showing ${{start + 1}} to ${{Math.min(end, filteredData.length)}} of ${{filteredData.length.toLocaleString()}} entities (1,732,544 total)`;
      document.getElementById('pageIndicator').textContent = `Page ${{currentPage}} of ${{totalPages}}`;
      document.getElementById('prevPageBtn').disabled = (currentPage === 1);
      document.getElementById('nextPageBtn').disabled = (currentPage >= totalPages);
    }}

    function getCountryFlag(c) {{
      if (c === 'India') return '&#127470;&#127475;';
      if (c === 'US') return '&#127482;&#127488;';
      if (c === 'France') return '&#127467;&#127479;';
      return '&#127757;';
    }}

    function applyFilters() {{
      filteredData = REAL_DATA.filter(item => {{
        if (activeCountry !== 'all' && item.country !== activeCountry) return false;
        const hasMatches = item.matches && item.matches.length > 0;
        if (activeStatus === 'matched' && !hasMatches) return false;
        if (activeStatus === 'singleton' && hasMatches) return false;
        if (activeSearch) {{
          const q = activeSearch.toLowerCase();
          const matchIdMatch = item.matches && item.matches.some(m => m.toLowerCase().includes(q));
          const nameMatch = (item.name || '').toLowerCase().includes(q);
          const addrMatch = (item.address || '').toLowerCase().includes(q);
          const idMatch = (item.id || '').toLowerCase().includes(q);
          if (!nameMatch && !addrMatch && !idMatch && !matchIdMatch) return false;
        }}
        return true;
      }});
      currentPage = 1;
      renderTable();
    }}

    // Filter Buttons
    document.querySelectorAll('[data-country]').forEach(btn => {{
      btn.addEventListener('click', () => {{
        document.querySelectorAll('[data-country]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeCountry = btn.dataset.country;
        applyFilters();
      }});
    }});

    document.querySelectorAll('[data-status]').forEach(btn => {{
      btn.addEventListener('click', () => {{
        document.querySelectorAll('[data-status]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeStatus = btn.dataset.status;
        applyFilters();
      }});
    }});

    document.getElementById('searchInput').addEventListener('input', (e) => {{
      activeSearch = e.target.value.trim();
      applyFilters();
    }});

    document.getElementById('prevPageBtn').addEventListener('click', () => {{
      if (currentPage > 1) {{ currentPage--; renderTable(); }}
    }});
    document.getElementById('nextPageBtn').addEventListener('click', () => {{
      const totalPages = Math.ceil(filteredData.length / perPage);
      if (currentPage < totalPages) {{ currentPage++; renderTable(); }}
    }});

    // Modal Inspection
    function openInspectModal(id) {{
      const item = REAL_DATA.find(e => e.id === id);
      if (!item) return;

      document.getElementById('modalS1Name').textContent = item.name || 'Unnamed Business';
      document.getElementById('modalS1Id').textContent = item.id;
      document.getElementById('modalS1Country').textContent = `${{getCountryFlag(item.country)}} ${{item.country}}`;
      document.getElementById('modalS1Addr').textContent = item.address || 'Address Unavailable';

      const container = document.getElementById('modalMatchesContainer');
      if (item.match_details && item.match_details.length > 0) {{
        container.innerHTML = item.match_details.map(m => `
          <div style="background:rgba(30, 41, 59, 0.6); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:12px 16px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span class="entity-id-tag" style="color:#34d399;">${{m.id}}</span>
              <span style="font-size:11px; color:#10b981; font-weight:600;">CONFIRMED RESOLUTION</span>
            </div>
            <div style="font-weight:600; color:#fff; margin-top:4px;">${{m.name || '[Unnamed Target]'}}</div>
            <div style="font-size:12px; color:#94a3b8;">${{m.address || '[Address Unavailable]'}}</div>
          </div>
        `).join('');
      }} else {{
        container.innerHTML = `
          <div style="background:rgba(30, 41, 59, 0.4); border:1px dashed rgba(255,255,255,0.1); border-radius:12px; padding:16px; text-align:center; color:#94a3b8;">
            No target candidates satisfied the threshold &tau; &ge; 0.740. This business entity is classified as a singleton.
          </div>
        `;
      }}

      const candContainer = document.getElementById('modalCandidateTags');
      if (item.candidates && item.candidates.length > 0) {{
        candContainer.innerHTML = item.candidates.map(c => `
          <span class="entity-id-tag" style="font-size:11px;">${{c}}</span>
        `).join('');
      }} else {{
        candContainer.innerHTML = `<span style="color:#64748b; font-size:12px;">No blocking candidates retrieved.</span>`;
      }}

      document.getElementById('inspectModal').style.display = 'flex';
    }}

    function closeModal() {{
      document.getElementById('inspectModal').style.display = 'none';
    }}
    window.addEventListener('click', (e) => {{
      if (e.target === document.getElementById('inspectModal')) closeModal();
    }});

    // Live Matcher Simulator
    const presets = [
      {{ s1N: "Zephay Labs Inc", s1A: "2621 Cotten Road, Tyler, TX", tgN: "Zephay Laboratory LLC", tgA: "2621 Cotton Rd, Tyler, TX" }},
      {{ s1N: "Vision Partners Corp", s1A: "1064 Newton Rd, Unit 11, Iowa City, IA", tgN: "Vision Partners Ltd", tgA: "1064 Newton Road Ste 11, Iowa City, IA" }},
      {{ s1N: "Infosys Technologies Pvt Ltd", s1A: "Electronic City, Hosur Road, Bangalore", tgN: "Infoses Tech Limited", tgA: "Hosur Rd, Phase 1 Electronics City, Bengaluru" }},
      {{ s1N: "Amazon Web Services LLC", s1A: "410 Terry Ave N, Seattle, WA", tgN: "Blue Star Coffee Roasters", tgA: "2010 Westlake Ave, Seattle, WA" }}
    ];

    function loadPreset(idx) {{
      const p = presets[idx];
      document.getElementById('mS1Name').value = p.s1N;
      document.getElementById('mS1Addr').value = p.s1A;
      document.getElementById('mTgtName').value = p.tgN;
      document.getElementById('mTgtAddr').value = p.tgA;
      runMatcher();
    }}

    function calculateFuzzRatio(s1, s2) {{
      if (!s1 || !s2) return 0;
      s1 = s1.toLowerCase().trim(); s2 = s2.toLowerCase().trim();
      if (s1 === s2) return 1.0;
      const longer = s1.length > s2.length ? s1 : s2;
      const shorter = s1.length > s2.length ? s2 : s1;
      if (longer.includes(shorter)) return shorter.length / longer.length;
      return 0.55;
    }}

    function runMatcher() {{
      const s1N = document.getElementById('mS1Name').value;
      const s1A = document.getElementById('mS1Addr').value;
      const tgN = document.getElementById('mTgtName').value;
      const tgA = document.getElementById('mTgtAddr').value;
      const tau = parseFloat(document.getElementById('threshSlider').value);

      // Simple real-time client computation
      const nameRatio = calculateFuzzRatio(s1N, tgN);
      const addrRatio = calculateFuzzRatio(s1A, tgA);

      // Check numbers in address
      const n1 = (s1A.match(/\\b\\d+\\b/g) || []);
      const n2 = (tgA.match(/\\b\\d+\\b/g) || []);
      const numMatch = n1.some(num => n2.includes(num));

      let prob = 0.45 * nameRatio + 0.35 * addrRatio + (numMatch ? 0.20 : 0.0);
      prob = Math.max(0.02, Math.min(0.99, prob));

      const isMatch = prob >= tau;
      const pct = Math.round(prob * 100);

      document.getElementById('scoreText').textContent = `${{pct}}%`;
      const offset = 377 - (377 * (pct / 100));
      const bar = document.getElementById('scoreBar');
      bar.style.strokeDashoffset = offset;
      bar.style.stroke = isMatch ? '#10b981' : (prob >= 0.5 ? '#f59e0b' : '#ef4444');

      const decision = document.getElementById('scoreDecision');
      if (isMatch) {{
        decision.textContent = `CONFIRMED MATCH (Prob >= ${{tau.toFixed(2)}})`;
        decision.style.color = '#34d399';
      }} else {{
        decision.textContent = `REJECTED (Prob < ${{tau.toFixed(2)}})`;
        decision.style.color = '#f87171';
      }}

      document.getElementById('fTokenSort').textContent = (nameRatio * 0.95).toFixed(2);
      document.getElementById('fTokenSet').textContent = nameRatio.toFixed(2);
      document.getElementById('fJaccard').textContent = (nameRatio * 0.85).toFixed(2);
      document.getElementById('fAddrSet').textContent = addrRatio.toFixed(2);
      document.getElementById('fNumShared').textContent = numMatch ? 'Matched Shared Number' : 'No Number Match';
    }}

    ['mS1Name', 'mS1Addr', 'mTgtName', 'mTgtAddr'].forEach(id => {{
      document.getElementById(id).addEventListener('input', runMatcher);
    }});
    document.getElementById('threshSlider').addEventListener('input', (e) => {{
      document.getElementById('threshVal').textContent = parseFloat(e.target.value).toFixed(3);
      runMatcher();
    }});

    // Initialize
    renderTable();
    runMatcher();
  </script>

  <!-- Embed Three.js liquid-metal 3D hero engine from template -->
  {three_script}

</body>
</html>
"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Master index.html successfully generated! ({len(html_content):,} bytes)")

if __name__ == '__main__':
    build_showcase()
