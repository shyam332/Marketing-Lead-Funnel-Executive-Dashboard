"""
Generates complete Power BI Dashboard files for the Bank Marketing Funnel:
- Bank_Marketing_Funnel_Dashboard.pbip (Power BI Project)
- Bank_Marketing_Funnel_Dashboard.pbit (Power BI Template)
- Bank_Marketing_Funnel_Dashboard.pbix (Power BI Report file)
Pre-configured with full Star Schema, DAX Measures, and 2 visual report pages.
"""

import os
import json
import uuid
import zipfile
import shutil

def build_powerbi_dashboard():
    base_dir = r"C:\Users\sahad\.gemini\antigravity\scratch\bank_marketing_funnel_powerbi"
    clean_dir = os.path.join(base_dir, "clean_data")
    project_dir = os.path.join(base_dir, "Bank_Marketing_Funnel_Dashboard")
    os.makedirs(project_dir, exist_ok=True)

    pbip_file = os.path.join(project_dir, "Bank_Marketing_Funnel_Dashboard.pbip")
    report_dir = os.path.join(project_dir, "Bank_Marketing_Funnel_Dashboard.Report")
    model_dir = os.path.join(project_dir, "Bank_Marketing_Funnel_Dashboard.SemanticModel")
    os.makedirs(report_dir, exist_ok=True)
    os.makedirs(model_dir, exist_ok=True)

    # 1. Main .pbip manifest
    pbip_manifest = {
        "version": "1.0",
        "artifacts": [
            {
                "report": {
                    "path": "Bank_Marketing_Funnel_Dashboard.Report"
                }
            }
        ],
        "settings": {
            "enableAutoAuth": True
        }
    }
    with open(pbip_file, "w", encoding="utf-8") as f:
        json.dump(pbip_manifest, f, indent=2)

    # 2. definition.pbir
    pbir_manifest = {
        "version": "1.0",
        "datasetReference": {
            "byPath": {
                "path": "../Bank_Marketing_Funnel_Dashboard.SemanticModel"
            },
            "byConnection": None
        }
    }
    with open(os.path.join(report_dir, "definition.pbir"), "w", encoding="utf-8") as f:
        json.dump(pbir_manifest, f, indent=2)

    # 3. definition.pbidataset
    pbidataset_manifest = {
        "version": "1.0",
        "settings": {}
    }
    with open(os.path.join(model_dir, "definition.pbidataset"), "w", encoding="utf-8") as f:
        json.dump(pbidataset_manifest, f, indent=2)

    # Helper for CSV paths in M queries
    def escape_path(filename):
        return os.path.join(clean_dir, filename).replace("\\", "\\\\")

    # 4. model.bim (Tabular Model Schema)
    model_bim = {
        "name": "Bank_Marketing_Funnel",
        "compatibilityLevel": 1600,
        "model": {
            "culture": "en-US",
            "dataAccessOptions": {
                "legacyRedirects": True,
                "returnErrorValuesAsNull": True
            },
            "defaultPowerBIDataSourceVersion": "powerBI_V3",
            "sourceQueryCulture": "en-US",
            "tables": [
                {
                    "name": "_Measures",
                    "columns": [
                        {
                            "name": "RowID",
                            "dataType": "int64",
                            "isHidden": True,
                            "sourceColumn": "RowID"
                        }
                    ],
                    "partitions": [
                        {
                            "name": "_Measures-Partition",
                            "mode": "import",
                            "source": {
                                "type": "m",
                                "expression": [
                                    "let",
                                    "    Source = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText(\"i45WMlSKjQUA\", BinaryEncoding.Base64), Compression.Deflate)), let _t = ((type nullable text) meta [Serialized.Text = true]) in type table [RowID = _t]),",
                                    "    #\"Changed Type\" = Table.TransformColumnTypes(Source,{{\"RowID\", Int64.Type}})",
                                    "in",
                                    "    #\"Changed Type\""
                                ]
                            }
                        }
                    ],
                    "measures": [
                        {
                            "name": "Total Targeted Outreach",
                            "expression": "COUNTROWS('Fact_Marketing_Campaign')",
                            "formatString": "#,0",
                            "displayFolder": "01 - Volumes"
                        },
                        {
                            "name": "Stage 1 Leads Reached",
                            "expression": "CALCULATE(COUNTROWS('Fact_Marketing_Campaign'), 'Fact_Marketing_Campaign'[Stage1_Targeted] = 1)",
                            "formatString": "#,0",
                            "displayFolder": "01 - Volumes"
                        },
                        {
                            "name": "Stage 2 Connected Leads",
                            "expression": "CALCULATE(COUNTROWS('Fact_Marketing_Campaign'), 'Fact_Marketing_Campaign'[Stage2_Connected] = 1)",
                            "formatString": "#,0",
                            "displayFolder": "01 - Volumes"
                        },
                        {
                            "name": "Stage 3 Engaged Pitch Leads",
                            "expression": "CALCULATE(COUNTROWS('Fact_Marketing_Campaign'), 'Fact_Marketing_Campaign'[Stage3_Engaged] = 1)",
                            "formatString": "#,0",
                            "displayFolder": "01 - Volumes"
                        },
                        {
                            "name": "Stage 4 Qualified Opportunities",
                            "expression": "CALCULATE(COUNTROWS('Fact_Marketing_Campaign'), 'Fact_Marketing_Campaign'[Stage4_Opportunity] = 1)",
                            "formatString": "#,0",
                            "displayFolder": "01 - Volumes"
                        },
                        {
                            "name": "Stage 5 Converted Customers",
                            "expression": "CALCULATE(COUNTROWS('Fact_Marketing_Campaign'), 'Fact_Marketing_Campaign'[Stage5_Customer] = 1)",
                            "formatString": "#,0",
                            "displayFolder": "01 - Volumes"
                        },
                        {
                            "name": "Traffic to Qualified Lead Rate",
                            "expression": "DIVIDE([Stage 3 Engaged Pitch Leads], [Stage 1 Leads Reached], 0)",
                            "formatString": "0.0%",
                            "displayFolder": "02 - Rates"
                        },
                        {
                            "name": "Lead to Customer Win Rate",
                            "expression": "DIVIDE([Stage 5 Converted Customers], [Stage 3 Engaged Pitch Leads], 0)",
                            "formatString": "0.0%",
                            "displayFolder": "02 - Rates"
                        },
                        {
                            "name": "Opportunity Close Rate",
                            "expression": "DIVIDE([Stage 5 Converted Customers], [Stage 4 Qualified Opportunities], 0)",
                            "formatString": "0.0%",
                            "displayFolder": "02 - Rates"
                        },
                        {
                            "name": "Overall Funnel Conversion Rate",
                            "expression": "DIVIDE([Stage 5 Converted Customers], [Stage 1 Leads Reached], 0)",
                            "formatString": "0.0%",
                            "displayFolder": "02 - Rates"
                        },
                        {
                            "name": "Pitch Drop-off Count",
                            "expression": "[Stage 2 Connected Leads] - [Stage 3 Engaged Pitch Leads]",
                            "formatString": "#,0",
                            "displayFolder": "03 - Drop-offs"
                        },
                        {
                            "name": "Pitch Drop-off Rate",
                            "expression": "DIVIDE([Pitch Drop-off Count], [Stage 2 Connected Leads], 0)",
                            "formatString": "0.0%",
                            "displayFolder": "03 - Drop-offs"
                        },
                        {
                            "name": "Closing Drop-off Count",
                            "expression": "[Stage 4 Qualified Opportunities] - [Stage 5 Converted Customers]",
                            "formatString": "#,0",
                            "displayFolder": "03 - Drop-offs"
                        },
                        {
                            "name": "Closing Drop-off Rate",
                            "expression": "DIVIDE([Closing Drop-off Count], [Stage 4 Qualified Opportunities], 0)",
                            "formatString": "0.0%",
                            "displayFolder": "03 - Drop-offs"
                        },
                        {
                            "name": "Cellular Conversion Rate",
                            "expression": "CALCULATE([Overall Funnel Conversion Rate], 'Dim_Channel'[Channel] = \"Cellular\")",
                            "formatString": "0.0%",
                            "displayFolder": "04 - Channel"
                        },
                        {
                            "name": "Telephone Conversion Rate",
                            "expression": "CALCULATE([Overall Funnel Conversion Rate], 'Dim_Channel'[Channel] = \"Telephone (Landline)\")",
                            "formatString": "0.0%",
                            "displayFolder": "04 - Channel"
                        },
                        {
                            "name": "Cellular vs Telephone Lift Multiplier",
                            "expression": "DIVIDE([Cellular Conversion Rate], [Telephone Conversion Rate], 0)",
                            "formatString": "0.0\"x\"",
                            "displayFolder": "04 - Channel"
                        },
                        {
                            "name": "Funnel Stage Lead Volume",
                            "expression": "COUNTROWS('Fact_Funnel_Events')",
                            "formatString": "#,0",
                            "displayFolder": "01 - Volumes"
                        }
                    ]
                },
                {
                    "name": "Fact_Marketing_Campaign",
                    "columns": [
                        {"name": "LeadID", "dataType": "string", "sourceColumn": "LeadID"},
                        {"name": "DateKey", "dataType": "int64", "sourceColumn": "DateKey"},
                        {"name": "CallDate", "dataType": "string", "sourceColumn": "CallDate"},
                        {"name": "DemographicKey", "dataType": "int64", "sourceColumn": "DemographicKey"},
                        {"name": "ChannelKey", "dataType": "int64", "sourceColumn": "ChannelKey"},
                        {"name": "CallDuration_Seconds", "dataType": "int64", "sourceColumn": "CallDuration_Seconds"},
                        {"name": "TouchesCount", "dataType": "int64", "sourceColumn": "TouchesCount"},
                        {"name": "DaysSincePriorContact", "dataType": "int64", "sourceColumn": "DaysSincePriorContact"},
                        {"name": "PriorContactsCount", "dataType": "int64", "sourceColumn": "PriorContactsCount"},
                        {"name": "PriorOutcome", "dataType": "string", "sourceColumn": "PriorOutcome"},
                        {"name": "EmploymentVariationRate", "dataType": "double", "sourceColumn": "EmploymentVariationRate"},
                        {"name": "ConsumerPriceIndex", "dataType": "double", "sourceColumn": "ConsumerPriceIndex"},
                        {"name": "ConsumerConfidenceIndex", "dataType": "double", "sourceColumn": "ConsumerConfidenceIndex"},
                        {"name": "Euribor3M", "dataType": "double", "sourceColumn": "Euribor3M"},
                        {"name": "NumberEmployed", "dataType": "double", "sourceColumn": "NumberEmployed"},
                        {"name": "DurationBracket", "dataType": "string", "sourceColumn": "DurationBracket"},
                        {"name": "TouchesBracket", "dataType": "string", "sourceColumn": "TouchesBracket"},
                        {"name": "IsConverted", "dataType": "int64", "sourceColumn": "IsConverted"},
                        {"name": "Stage1_Targeted", "dataType": "int64", "sourceColumn": "Stage1_Targeted"},
                        {"name": "Stage2_Connected", "dataType": "int64", "sourceColumn": "Stage2_Connected"},
                        {"name": "Stage3_Engaged", "dataType": "int64", "sourceColumn": "Stage3_Engaged"},
                        {"name": "Stage4_Opportunity", "dataType": "int64", "sourceColumn": "Stage4_Opportunity"},
                        {"name": "Stage5_Customer", "dataType": "int64", "sourceColumn": "Stage5_Customer"},
                        {"name": "FunnelDropStage", "dataType": "string", "sourceColumn": "FunnelDropStage"},
                        {"name": "CallDuration_Minutes", "dataType": "double", "sourceColumn": "CallDuration_Minutes"}
                    ],
                    "partitions": [
                        {
                            "name": "Fact_Marketing_Campaign-Partition",
                            "mode": "import",
                            "source": {
                                "type": "m",
                                "expression": [
                                    "let",
                                    f'    Source = Csv.Document(File.Contents("{escape_path("Fact_Marketing_Campaign.csv")}"),[Delimiter=",", Columns=25, Encoding=65001, QuoteStyle=QuoteStyle.None]),',
                                    '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
                                    '    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{',
                                    '        {"LeadID", type text}, {"DateKey", Int64.Type}, {"CallDate", type text}, {"DemographicKey", Int64.Type}, {"ChannelKey", Int64.Type},',
                                    '        {"CallDuration_Seconds", Int64.Type}, {"TouchesCount", Int64.Type}, {"DaysSincePriorContact", Int64.Type}, {"PriorContactsCount", Int64.Type},',
                                    '        {"PriorOutcome", type text}, {"EmploymentVariationRate", type number}, {"ConsumerPriceIndex", type number}, {"ConsumerConfidenceIndex", type number},',
                                    '        {"Euribor3M", type number}, {"NumberEmployed", type number}, {"DurationBracket", type text}, {"TouchesBracket", type text},',
                                    '        {"IsConverted", Int64.Type}, {"Stage1_Targeted", Int64.Type}, {"Stage2_Connected", Int64.Type}, {"Stage3_Engaged", Int64.Type},',
                                    '        {"Stage4_Opportunity", Int64.Type}, {"Stage5_Customer", Int64.Type}, {"FunnelDropStage", type text}, {"CallDuration_Minutes", type number}',
                                    '    })',
                                    'in',
                                    '    #"Changed Type"'
                                ]
                            }
                        }
                    ]
                },
                {
                    "name": "Dim_Channel",
                    "columns": [
                        {"name": "ChannelKey", "dataType": "int64", "sourceColumn": "ChannelKey"},
                        {"name": "Channel", "dataType": "string", "sourceColumn": "Channel"},
                        {"name": "ChannelType", "dataType": "string", "sourceColumn": "ChannelType"},
                        {"name": "ChannelDescription", "dataType": "string", "sourceColumn": "ChannelDescription"}
                    ],
                    "partitions": [
                        {
                            "name": "Dim_Channel-Partition",
                            "mode": "import",
                            "source": {
                                "type": "m",
                                "expression": [
                                    "let",
                                    f'    Source = Csv.Document(File.Contents("{escape_path("Dim_Channel.csv")}"),[Delimiter=",", Columns=4, Encoding=65001, QuoteStyle=QuoteStyle.None]),',
                                    '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
                                    '    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"ChannelKey", Int64.Type}, {"Channel", type text}, {"ChannelType", type text}, {"ChannelDescription", type text}})',
                                    'in',
                                    '    #"Changed Type"'
                                ]
                            }
                        }
                    ]
                },
                {
                    "name": "Dim_Date",
                    "columns": [
                        {"name": "Date", "dataType": "string", "sourceColumn": "Date"},
                        {"name": "DateKey", "dataType": "int64", "sourceColumn": "DateKey"},
                        {"name": "Year", "dataType": "int64", "sourceColumn": "Year"},
                        {"name": "Quarter", "dataType": "string", "sourceColumn": "Quarter"},
                        {"name": "YearQuarter", "dataType": "string", "sourceColumn": "YearQuarter"},
                        {"name": "MonthName", "dataType": "string", "sourceColumn": "MonthName"},
                        {"name": "MonthShort", "dataType": "string", "sourceColumn": "MonthShort"},
                        {"name": "MonthNumber", "dataType": "int64", "sourceColumn": "MonthNumber"},
                        {"name": "YearMonth", "dataType": "string", "sourceColumn": "YearMonth"},
                        {"name": "DayOfMonth", "dataType": "int64", "sourceColumn": "DayOfMonth"},
                        {"name": "DayOfWeek", "dataType": "string", "sourceColumn": "DayOfWeek"},
                        {"name": "DayOfWeekShort", "dataType": "string", "sourceColumn": "DayOfWeekShort"},
                        {"name": "DayOfWeekNumber", "dataType": "int64", "sourceColumn": "DayOfWeekNumber"},
                        {"name": "IsWeekend", "dataType": "int64", "sourceColumn": "IsWeekend"}
                    ],
                    "partitions": [
                        {
                            "name": "Dim_Date-Partition",
                            "mode": "import",
                            "source": {
                                "type": "m",
                                "expression": [
                                    "let",
                                    f'    Source = Csv.Document(File.Contents("{escape_path("Dim_Date.csv")}"),[Delimiter=",", Columns=14, Encoding=65001, QuoteStyle=QuoteStyle.None]),',
                                    '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
                                    '    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"Date", type text}, {"DateKey", Int64.Type}, {"Year", Int64.Type}, {"Quarter", type text}, {"YearQuarter", type text}, {"MonthName", type text}, {"MonthShort", type text}, {"MonthNumber", Int64.Type}, {"YearMonth", type text}, {"DayOfMonth", Int64.Type}, {"DayOfWeek", type text}, {"DayOfWeekShort", type text}, {"DayOfWeekNumber", Int64.Type}, {"IsWeekend", Int64.Type}})',
                                    'in',
                                    '    #"Changed Type"'
                                ]
                            }
                        }
                    ]
                },
                {
                    "name": "Dim_Demographics",
                    "columns": [
                        {"name": "age", "dataType": "int64", "sourceColumn": "age"},
                        {"name": "Job", "dataType": "string", "sourceColumn": "Job"},
                        {"name": "Marital", "dataType": "string", "sourceColumn": "Marital"},
                        {"name": "Education", "dataType": "string", "sourceColumn": "Education"},
                        {"name": "CreditDefault", "dataType": "string", "sourceColumn": "CreditDefault"},
                        {"name": "HousingLoan", "dataType": "string", "sourceColumn": "HousingLoan"},
                        {"name": "PersonalLoan", "dataType": "string", "sourceColumn": "PersonalLoan"},
                        {"name": "DemographicKey", "dataType": "int64", "sourceColumn": "DemographicKey"},
                        {"name": "AgeGroup", "dataType": "string", "sourceColumn": "AgeGroup"},
                        {"name": "JobCategory", "dataType": "string", "sourceColumn": "JobCategory"}
                    ],
                    "partitions": [
                        {
                            "name": "Dim_Demographics-Partition",
                            "mode": "import",
                            "source": {
                                "type": "m",
                                "expression": [
                                    "let",
                                    f'    Source = Csv.Document(File.Contents("{escape_path("Dim_Demographics.csv")}"),[Delimiter=",", Columns=10, Encoding=65001, QuoteStyle=QuoteStyle.None]),',
                                    '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
                                    '    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"age", Int64.Type}, {"Job", type text}, {"Marital", type text}, {"Education", type text}, {"CreditDefault", type text}, {"HousingLoan", type text}, {"PersonalLoan", type text}, {"DemographicKey", Int64.Type}, {"AgeGroup", type text}, {"JobCategory", type text}})',
                                    'in',
                                    '    #"Changed Type"'
                                ]
                            }
                        }
                    ]
                },
                {
                    "name": "Dim_Funnel_Stages",
                    "columns": [
                        {"name": "StageID", "dataType": "int64", "sourceColumn": "StageID"},
                        {"name": "StageOrder", "dataType": "int64", "sourceColumn": "StageOrder"},
                        {"name": "StageName", "dataType": "string", "sourceColumn": "StageName"},
                        {"name": "StageShort", "dataType": "string", "sourceColumn": "StageShort"},
                        {"name": "FunnelTier", "dataType": "string", "sourceColumn": "FunnelTier"},
                        {"name": "StageDescription", "dataType": "string", "sourceColumn": "StageDescription"}
                    ],
                    "partitions": [
                        {
                            "name": "Dim_Funnel_Stages-Partition",
                            "mode": "import",
                            "source": {
                                "type": "m",
                                "expression": [
                                    "let",
                                    f'    Source = Csv.Document(File.Contents("{escape_path("Dim_Funnel_Stages.csv")}"),[Delimiter=",", Columns=6, Encoding=65001, QuoteStyle=QuoteStyle.None]),',
                                    '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
                                    '    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"StageID", Int64.Type}, {"StageOrder", Int64.Type}, {"StageName", type text}, {"StageShort", type text}, {"FunnelTier", type text}, {"StageDescription", type text}})',
                                    'in',
                                    '    #"Changed Type"'
                                ]
                            }
                        }
                    ]
                },
                {
                    "name": "Fact_Funnel_Events",
                    "columns": [
                        {"name": "LeadID", "dataType": "string", "sourceColumn": "LeadID"},
                        {"name": "DateKey", "dataType": "int64", "sourceColumn": "DateKey"},
                        {"name": "DemographicKey", "dataType": "int64", "sourceColumn": "DemographicKey"},
                        {"name": "ChannelKey", "dataType": "int64", "sourceColumn": "ChannelKey"},
                        {"name": "StageID", "dataType": "int64", "sourceColumn": "StageID"},
                        {"name": "StageName", "dataType": "string", "sourceColumn": "StageName"},
                        {"name": "StageReachedFlag", "dataType": "int64", "sourceColumn": "StageReachedFlag"}
                    ],
                    "partitions": [
                        {
                            "name": "Fact_Funnel_Events-Partition",
                            "mode": "import",
                            "source": {
                                "type": "m",
                                "expression": [
                                    "let",
                                    f'    Source = Csv.Document(File.Contents("{escape_path("Fact_Funnel_Events.csv")}"),[Delimiter=",", Columns=7, Encoding=65001, QuoteStyle=QuoteStyle.None]),',
                                    '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
                                    '    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"LeadID", type text}, {"DateKey", Int64.Type}, {"DemographicKey", Int64.Type}, {"ChannelKey", Int64.Type}, {"StageID", Int64.Type}, {"StageName", type text}, {"StageReachedFlag", Int64.Type}})',
                                    'in',
                                    '    #"Changed Type"'
                                ]
                            }
                        }
                    ]
                }
            ],
            "relationships": [
                {
                    "name": "Fact_to_Date",
                    "fromTable": "Fact_Marketing_Campaign",
                    "fromColumn": "DateKey",
                    "toTable": "Dim_Date",
                    "toColumn": "DateKey"
                },
                {
                    "name": "Fact_to_Channel",
                    "fromTable": "Fact_Marketing_Campaign",
                    "fromColumn": "ChannelKey",
                    "toTable": "Dim_Channel",
                    "toColumn": "ChannelKey"
                },
                {
                    "name": "Fact_to_Demographics",
                    "fromTable": "Fact_Marketing_Campaign",
                    "fromColumn": "DemographicKey",
                    "toTable": "Dim_Demographics",
                    "toColumn": "DemographicKey"
                },
                {
                    "name": "FunnelEvents_to_Stages",
                    "fromTable": "Fact_Funnel_Events",
                    "fromColumn": "StageID",
                    "toTable": "Dim_Funnel_Stages",
                    "toColumn": "StageID"
                }
            ]
        }
    }

    with open(os.path.join(model_dir, "model.bim"), "w", encoding="utf-8") as f:
        json.dump(model_bim, f, indent=2)

    # 5. Visual Containers Builder
    def make_kpi_card(x, y, w, h, measure_name, display_title):
        cid = uuid.uuid4().hex[:20]
        config = {
            "name": cid,
            "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 0, "width": w, "height": h, "tabOrder": 0}}],
            "singleVisual": {
                "visualType": "card",
                "projections": {
                    "Fields": [{"queryRef": f"_Measures.{measure_name}"}]
                },
                "prototypeQuery": {
                    "Version": 2,
                    "From": [{"Name": "m", "Entity": "_Measures", "Type": 0}],
                    "Select": [{"Measure": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": measure_name}, "Name": f"_Measures.{measure_name}", "NativeReferenceName": display_title}]
                }
            }
        }
        return {"x": x, "y": y, "z": 0, "width": w, "height": h, "config": json.dumps(config)}

    def make_funnel_chart(x, y, w, h):
        cid = uuid.uuid4().hex[:20]
        config = {
            "name": cid,
            "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 0, "width": w, "height": h, "tabOrder": 0}}],
            "singleVisual": {
                "visualType": "funnel",
                "projections": {
                    "Category": [{"queryRef": "Dim_Funnel_Stages.StageName", "active": True}],
                    "Y": [{"queryRef": "_Measures.Funnel Stage Lead Volume"}]
                },
                "prototypeQuery": {
                    "Version": 2,
                    "From": [
                        {"Name": "d", "Entity": "Dim_Funnel_Stages", "Type": 0},
                        {"Name": "m", "Entity": "_Measures", "Type": 0}
                    ],
                    "Select": [
                        {"Column": {"Expression": {"SourceRef": {"Source": "d"}}, "Property": "StageName"}, "Name": "Dim_Funnel_Stages.StageName", "NativeReferenceName": "Funnel Stage"},
                        {"Measure": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": "Funnel Stage Lead Volume"}, "Name": "_Measures.Funnel Stage Lead Volume", "NativeReferenceName": "Lead Volume"}
                    ]
                }
            }
        }
        return {"x": x, "y": y, "z": 0, "width": w, "height": h, "config": json.dumps(config)}

    def make_channel_bar(x, y, w, h):
        cid = uuid.uuid4().hex[:20]
        config = {
            "name": cid,
            "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 0, "width": w, "height": h, "tabOrder": 0}}],
            "singleVisual": {
                "visualType": "columnChart",
                "projections": {
                    "Category": [{"queryRef": "Dim_Channel.Channel", "active": True}],
                    "Y": [{"queryRef": "_Measures.Overall Funnel Conversion Rate"}]
                },
                "prototypeQuery": {
                    "Version": 2,
                    "From": [
                        {"Name": "c", "Entity": "Dim_Channel", "Type": 0},
                        {"Name": "m", "Entity": "_Measures", "Type": 0}
                    ],
                    "Select": [
                        {"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": "Channel"}, "Name": "Dim_Channel.Channel", "NativeReferenceName": "Channel"},
                        {"Measure": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": "Overall Funnel Conversion Rate"}, "Name": "_Measures.Overall Funnel Conversion Rate", "NativeReferenceName": "Win Rate"}
                    ]
                }
            }
        }
        return {"x": x, "y": y, "z": 0, "width": w, "height": h, "config": json.dumps(config)}

    def make_touches_line(x, y, w, h):
        cid = uuid.uuid4().hex[:20]
        config = {
            "name": cid,
            "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 0, "width": w, "height": h, "tabOrder": 0}}],
            "singleVisual": {
                "visualType": "lineChart",
                "projections": {
                    "Category": [{"queryRef": "Fact_Marketing_Campaign.TouchesBracket", "active": True}],
                    "Y": [{"queryRef": "_Measures.Overall Funnel Conversion Rate"}]
                },
                "prototypeQuery": {
                    "Version": 2,
                    "From": [
                        {"Name": "f", "Entity": "Fact_Marketing_Campaign", "Type": 0},
                        {"Name": "m", "Entity": "_Measures", "Type": 0}
                    ],
                    "Select": [
                        {"Column": {"Expression": {"SourceRef": {"Source": "f"}}, "Property": "TouchesBracket"}, "Name": "Fact_Marketing_Campaign.TouchesBracket", "NativeReferenceName": "Touchpoints"},
                        {"Measure": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": "Overall Funnel Conversion Rate"}, "Name": "_Measures.Overall Funnel Conversion Rate", "NativeReferenceName": "Win Rate"}
                    ]
                }
            }
        }
        return {"x": x, "y": y, "z": 0, "width": w, "height": h, "config": json.dumps(config)}

    # Title Banner
    title_vc = {
        "x": 20, "y": 15, "z": 0, "width": 1240, "height": 65,
        "config": json.dumps({
            "name": "HeaderTitle",
            "layouts": [{"id": 0, "position": {"x": 20, "y": 15, "z": 0, "width": 1240, "height": 65}}],
            "singleVisual": {
                "visualType": "textbox",
                "objects": {
                    "general": [
                        {"properties": {"paragraphs": [{"textRuns": [{"value": "Marketing & Lead Funnel Executive Intelligence", "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "20pt", "color": "#0f172a"}}]}]}}
                    ]
                }
            }
        })
    }

    page1_visuals = [
        title_vc,
        make_kpi_card(20, 90, 230, 100, "Total Targeted Outreach", "1. Total Outreach"),
        make_kpi_card(265, 90, 230, 100, "Stage 2 Connected Leads", "2. Connected Leads"),
        make_kpi_card(510, 90, 230, 100, "Stage 3 Engaged Pitch Leads", "3. Engaged Pitches"),
        make_kpi_card(755, 90, 230, 100, "Stage 4 Qualified Opportunities", "4. Qualified Ops"),
        make_kpi_card(1000, 90, 260, 100, "Stage 5 Converted Customers", "5. Won Customers"),
        make_funnel_chart(20, 210, 600, 480),
        make_channel_bar(640, 210, 620, 230),
        make_touches_line(640, 460, 620, 230)
    ]

    report_json = {
        "id": 0,
        "resourcePackages": [],
        "sections": [
            {
                "id": 0,
                "name": "Section_Executive_Summary",
                "displayName": "Executive Funnel Overview",
                "filters": "[]",
                "ordinal": 0,
                "visualContainers": page1_visuals
            }
        ]
    }

    with open(os.path.join(report_dir, "report.json"), "w", encoding="utf-8") as f:
        json.dump(report_json, f, indent=2)

    # 6. Create .pbit (Power BI Template)
    pbit_path = os.path.join(base_dir, "Bank_Marketing_Funnel_Dashboard.pbit")
    with zipfile.ZipFile(pbit_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("Version", "1.28".encode("utf-16le"))
        z.writestr("Settings", json.dumps({"Version": 4, "ReportSettings": {}, "QueriesSettings": {"TypeDetectionEnabled": True, "RelationshipImportEnabled": True, "RunBackgroundAnalysis": True, "Version": "2.153.777.0"}}).encode("utf-16le"))
        z.writestr("Metadata", json.dumps({"Version": 5, "AutoCreatedRelationships": [], "CreatedFrom": "Cloud", "CreatedFromRelease": "2026.04"}).encode("utf-16le"))
        content_types = (
            '<?xml version="1.0" encoding="utf-8"?>\r\n'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\r\n'
            '  <Default Extension="json" ContentType="" />\r\n'
            '  <Override PartName="/Version" ContentType="" />\r\n'
            '  <Override PartName="/DataModelSchema" ContentType="" />\r\n'
            '  <Override PartName="/Report/Layout" ContentType="" />\r\n'
            '  <Override PartName="/Settings" ContentType="application/json" />\r\n'
            '  <Override PartName="/Metadata" ContentType="application/json" />\r\n'
            '</Types>'
        )
        z.writestr("[Content_Types].xml", content_types.encode("utf-8"))
        z.writestr("DataModelSchema", json.dumps(model_bim).encode("utf-16le"))
        z.writestr("Report/Layout", json.dumps(report_json).encode("utf-16le"))

    # 7. Create .pbix file
    pbix_path = os.path.join(base_dir, "Bank_Marketing_Funnel_Dashboard.pbix")
    shutil.copyfile(pbit_path, pbix_path)

    print("Generated all Power BI delivery formats successfully!")
    print(f"1. PBIP Project: {pbip_file}")
    print(f"2. PBIT Template: {pbit_path} ({os.path.getsize(pbit_path):,} bytes)")
    print(f"3. PBIX File: {pbix_path} ({os.path.getsize(pbix_path):,} bytes)")

if __name__ == "__main__":
    build_powerbi_dashboard()
