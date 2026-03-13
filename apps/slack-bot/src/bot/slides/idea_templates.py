"""
Templates d'idées créatives pour la génération de présentations
Séparés du code principal pour réduire la complexité
"""

IDEA_TEMPLATES = [
    {
        'name': "{brand_name} Digital Experience",
        'trend': "Digital transformation",
        'opportunity': "Enhanced customer engagement",
        'mechanism': "Interactive digital platform",
        'components': ["Mobile app", "Social integration", "Personalization"],
        'amplification': "Viral sharing features",
        'viral': ["User-generated content", "Social challenges", "Influencer partnerships"],
        'partnerships': "Tech and creative agencies",
        'visual': "Modern, clean aesthetic",
        'colors': ["#2C3E50", "#3498DB", "#E74C3C"],
        'imagery': "Professional lifestyle photography",
        'implementation': "6-month development cycle",
        'channels': ["Digital", "Social", "Mobile"],
        'timeline': "Q1-Q2 2025",
        'resources': "Development team, creative agency",
        'outcomes': ["Increased engagement", "Brand awareness", "Lead generation"],
        'kpis': [{"metric": "App downloads", "target": "10K"}, {"metric": "Engagement rate", "target": "25%"}],
        'roi': "300% projected return"
    },
    {
        'name': "{brand_name} Community Activation",
        'trend': "Community building",
        'opportunity': "Brand loyalty and advocacy",
        'mechanism': "Community platform and events",
        'components': ["Online community", "Live events", "Exclusive content"],
        'amplification': "Member-to-member sharing",
        'viral': ["Community challenges", "User testimonials", "Event coverage"],
        'partnerships': "Community platforms and event organizers",
        'visual': "Warm, inclusive aesthetic",
        'colors': ["#F39C12", "#E67E22", "#D35400"],
        'imagery': "Community and lifestyle photography",
        'implementation': "3-month setup phase",
        'channels': ["Community", "Events", "Social"],
        'timeline': "Q2-Q3 2025",
        'resources': "Community manager, event coordinator",
        'outcomes': ["Community growth", "Brand loyalty", "Word-of-mouth"],
        'kpis': [{"metric": "Community members", "target": "5K"}, {"metric": "Event attendance", "target": "500"}],
        'roi': "250% projected return"
    },
    {
        'name': "{brand_name} Sustainability Initiative",
        'trend': "Environmental consciousness",
        'opportunity': "Brand differentiation and purpose",
        'mechanism': "Sustainable practices and storytelling",
        'components': ["Sustainable packaging", "Carbon offset", "Transparency"],
        'amplification': "Social proof and storytelling",
        'viral': ["Environmental challenges", "User testimonials", "Impact reporting"],
        'partnerships': "Environmental organizations and influencers",
        'visual': "Natural, organic aesthetic",
        'colors': ["#27AE60", "#2ECC71", "#F1C40F"],
        'imagery': "Nature and sustainable lifestyle photography",
        'implementation': "4-month implementation",
        'channels': ["Social", "Content", "PR"],
        'timeline': "Q3-Q4 2025",
        'resources': "Sustainability consultant, content creator",
        'outcomes': ["Brand differentiation", "Customer loyalty", "PR coverage"],
        'kpis': [{"metric": "Sustainability mentions", "target": "50"}, {"metric": "Engagement rate", "target": "30%"}],
        'roi': "200% projected return"
    }
]

def get_idea_templates() -> list:
    """Retourne la liste des templates d'idées"""
    return IDEA_TEMPLATES.copy()

def customize_template(template: dict, brand_name: str) -> dict:
    """Personnalise un template avec le nom de la marque"""
    customized = template.copy()
    customized['name'] = template['name'].format(brand_name=brand_name)
    return customized
