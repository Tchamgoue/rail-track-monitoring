# -*- coding: utf-8 -*-
"""
Exportation des données dans différents formats
"""

import csv
from io import StringIO
from datetime import datetime


def export_inspections_to_csv(inspections):
    """
    Exporte une liste d'inspections en CSV
    
    Args:
        inspections: Liste d'objets Inspection
        
    Returns:
        str: Contenu CSV
    """
    output = StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow([
        'ID',
        'Filename',
        'Upload Date',
        'Anomalies Count',
        'Criticality Score',
        'Criticality Level',
        'Processing Time (s)',
        'Notes'
    ])
    
    # Data
    for insp in inspections:
        writer.writerow([
            insp.id,
            insp.original_filename,
            insp.upload_date,
            insp.anomalies_count,
            insp.criticality_score,
            insp.get_criticality_level(),
            insp.processing_time,
            insp.notes
        ])
    
    return output.getvalue()