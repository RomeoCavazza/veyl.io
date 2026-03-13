#!/usr/bin/env python3
"""
Script d'analyse détaillée de la structure Havana Club
Identifie précisément les 57 slides uniques
"""

from src.bot.parser.pdf_parser import extract_text_from_pdf
import re

def analyze_havana_structure():
    """Analyse complète de la structure Havana Club - 57 slides"""
    
    print("=== ANALYSE COMPLÈTE - RECO HAVANA CLUB (57 SLIDES) ===")
    
    # Extraction du texte
    text = extract_text_from_pdf('Examples/RECO/RECO HAVANA CLUB.pdf')
    pages = text.split('--- Page')
    
    print(f"Nombre total de pages: {len(pages)-1}")
    
    # Analyse slide par slide
    slides_analysis = []
    
    for i, page in enumerate(pages[1:], 1):
        content = page.strip()
        if not content:
            continue
            
        # Identifier le contenu principal (ignorer les headers répétés)
        main_content = content[content.find('\n')+1:] if '\n' in content else content
        main_content = main_content[:500]  # Premier 500 caractères pour identifier
        
        slide_info = {
            'page': i,
            'type': 'Unknown',
            'title': '',
            'content_preview': main_content[:200] + '...' if len(main_content) > 200 else main_content
        }
        
        # Identification du type de slide
        if 'havana club revolvr awareness activation 2025' in content.lower() and 'killing it since 2010' in content.lower() and len(content.strip()) < 200:
            slide_info['type'] = 'Cover'
            slide_info['title'] = 'Cover - Havana Club Awareness Activation 2025'
        elif 'strategic priorities' in content.lower():
            slide_info['type'] = 'Strategic Priorities'
            slide_info['title'] = 'Strategic Priorities'
        elif '1. brand overview' in content.lower() and '2. state of play' in content.lower() and '3. idea #1' in content.lower():
            slide_info['type'] = 'Sommaire'
            slide_info['title'] = 'Sommaire'
        elif 'brand overview' in content.lower() and 'current perception' in content.lower():
            slide_info['type'] = 'Brand Overview'
            slide_info['title'] = 'Brand Overview - Current Perception'
        elif 'competitor' in content.lower() and 'alcohol market' in content.lower():
            slide_info['type'] = 'Competitor Analysis'
            slide_info['title'] = 'Competitor Analysis - Alcohol Market'
        elif 'personae' in content.lower() or 'social connector' in content.lower():
            slide_info['type'] = 'Persona'
            slide_info['title'] = 'Havana Club Persona'
        elif 'bacardí' in content.lower() and 'rum month' in content.lower():
            slide_info['type'] = 'Competitor Analysis'
            slide_info['title'] = 'Bacardí Analysis'
        elif 'captain morgan' in content.lower():
            slide_info['type'] = 'Competitor Analysis'
            slide_info['title'] = 'Captain Morgan Analysis'
        elif 'idea #1' in content.lower() and 'cultural trends' in content.lower():
            slide_info['type'] = 'Idea #1'
            slide_info['title'] = 'Idea #1 - Cultural Trends'
        elif 'idea #2' in content.lower() and 'tiktok trends' in content.lower():
            slide_info['type'] = 'Idea #2'
            slide_info['title'] = 'Idea #2 - TikTok Trends'
        elif 'idea #3' in content.lower() and 'societal trends' in content.lower():
            slide_info['type'] = 'Idea #3'
            slide_info['title'] = 'Idea #3 - Societal Trends'
        elif 'timeline' in content.lower() and ('2025' in content.lower() or 'january' in content.lower() or 'february' in content.lower()):
            slide_info['type'] = 'Timeline'
            slide_info['title'] = 'Timeline'
        elif 'budget' in content.lower() and ('€' in content.lower() or 'euro' in content.lower() or 'cost' in content.lower()):
            slide_info['type'] = 'Budget'
            slide_info['title'] = 'Budget'
        elif len(content.strip()) < 100:
            slide_info['type'] = 'Visual/Image'
            slide_info['title'] = 'Visual Slide'
        else:
            slide_info['type'] = 'Content'
            slide_info['title'] = f'Content Slide {i}'
        
        slides_analysis.append(slide_info)
    
    # Compter par type
    type_counts = {}
    for slide in slides_analysis:
        slide_type = slide['type']
        type_counts[slide_type] = type_counts.get(slide_type, 0) + 1
    
    print(f"\n=== RÉPARTITION DES 57 SLIDES ===")
    total_counted = 0
    for slide_type, count in sorted(type_counts.items()):
        print(f"{slide_type}: {count} slides")
        total_counted += count
    
    print(f"\nTotal slides identifiées: {total_counted}")
    
    # Afficher les détails des slides
    print(f"\n=== DÉTAIL DES SLIDES ===")
    for slide in slides_analysis[:20]:  # Afficher les 20 premières
        print(f"Page {slide['page']}: {slide['type']} - {slide['title']}")
        print(f"  Preview: {slide['content_preview'][:100]}...")
        print()
    
    if len(slides_analysis) > 20:
        print(f"... et {len(slides_analysis) - 20} slides supplémentaires")
    
    return slides_analysis, type_counts

if __name__ == "__main__":
    analyze_havana_structure() 