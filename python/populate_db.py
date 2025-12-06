'''
This is the script we used to populate our ChromaDB database with data scraped from various URLs about Ghana.
It contains all the datasets we used that we compiled and origanized in this link: https://1drv.ms/x/c/9a10fc8cf20e2bd5/IQCJ7CzUe-ImQLLnsrN7ImpNAcggdCkc0al-l4MWWXJOyEU?e=m2885E

We also had some that were pdfs so we downloaded them and added it in the folder pdf_datasets.


'''



#All Imports

import time
import chromadb
from chroma_utilities import *
from chromadb.utils import embedding_functions



#For the main program, we used vector_db as the ChromaDB path so we maintain consistency by populating our datasets into the same path.
CHROMA_PATH = "../vector_db"
PDF_DATASETS_PATH = "../pdf_datasets"


#These are our target URLs to scrape data from.
urls_to_scrape = [
    "https://www.bbc.com/news/world-africa-13433790",
    "https://whc.unesco.org/en/list/34/",
    "https://oxfordre.com/africanhistory/view/10.1093/acrefore/9780190277734.001.0001/acrefore-9780190277734-e-1360?print=pdf",
    "http://aanma.gov.gh/documents/1992%20Constitution%20of%20Ghana.pdf",
    "https://gse.com.gh/overview/",
    "https://mofep.gov.gh/sites/default/files/budget-statements/2026-Budget-Statement-and-Economic-Policy.pdf",
    "https://blogs.worldbank.org/en/nasikiliza/how-ghana-improving-learning-every-child",
    "https://www.worldbank.org/en/results/2021/01/05/increasing-access-to-quality-secondary-education-to-the-poorest-districts-ghanas-experience-with-results-based-financing-in-education",
    "https://www.worldbank.org/en/results/2022/05/16/afw-ghana-online-education-for-delivering-learning-outcomes-during-the-covid-19-school-closure",
    "https://www.iicba.unesco.org/en/ghana",
    "https://www.ceicdata.com/en/ghana/education-statistics",
    "https://www.gtec.edu.gh/download/file/Journal%20Vol%208%20FullDoc%20October%2017.pdf",
    "https://statsghana.gov.gh/gssmain/fileUpload/pressrelease/NATIONAL_EDUCATION_REPORT_FINAL_24.3.25_OS.pdf",
    "https://waecgh.org/2025/09/05/press-briefing-on-the-conduct-of-the-basic-education-certificate-examination-for-school-and-private-candidates-2025-and-the-west-african-senior-school-certificate-examination-wassce-for-school-cand/",
    "https://sapghana.com/data/documents/Ghana-Education-Sector-Analysis-2018.pdf",
    "https://ges.gov.gh/page.php?slug=history",
    "https://ges.gov.gh/page.php?slug=organisational-structure",
    "https://ges.gov.gh/page.php?slug=mandate-vision",
    "https://www.worldbank.org/en/news/press-release/2024/04/30/new-world-bank-report-calls-for-strengthening-resilience-of-ghana-health-system-in-response-to-climate-change",
    "https://kbth.gov.gh/a-brief-history/",
    "https://dhsprogram.com/pubs/pdf/spa6/02chapter02.pdf",
    "https://www.moh.gov.gh/ghana-says-no-to-cervical-cancer-with-free-hpv-vaccine-for-girls/",
    "https://ghs.gov.gh/news-and-events/ghana-records-marginal-increase-in-maternal-mortality-rate",
    "https://ghs.gov.gh/news-and-events/ghana-korea-health-ties-strengthened-as-ag-dg-ghs-receives-diplomatic-medal",
    "https://ghs.gov.gh/about-us",
    "https://www.moh.gov.gh/ministry-of-health-hosts-uk-trade-envoy-to-explore-health-sector-partnerships/",
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC5443676/",
    "https://link.springer.com/article/10.1186/s12960-021-00590-3",
    "https://journals.sagepub.com/doi/pdf/10.4081/jphr.2021.2448",
    "https://gsa.gov.gh/history/",
    "https://gsa.gov.gh/gsa-functions/",
    "https://gsa.gov.gh/about/",
    "https://fdaghana.gov.gh/wp-content/uploads/2025/04/DOES-THE-COLOUR-OF-PALM-OIL-REALLY-MATTER-WHEN-PURCHASING-PALM-OIL.pdf",
    "https://fdaghana.gov.gh/wp-content/uploads/2025/04/National-FoSERP-Document.pdf",
    "https://fdaghana.gov.gh/wp-content/uploads/2025/04/NFSP-Document.pdf",
    "https://microdata.worldbank.org/index.php/catalog/6122",
    "https://www.graphic.com.gh/news/health/over-334-700-people-living-with-hiv-in-ghana.html",
    "https://www.cell.com/heliyon/fulltext/S2405-8440(23)02698-1",
    "https://curriculumresources.edu.gh/wp-content/uploads/2025/01/Geography_Section-10-TV.pdf",
    "https://www.easytrackghana.com/travel-information-ghana-climate-calendar.php",
    "https://www.mdpi.com/2225-1154/3/1/78",
    "https://www.bluegreenatlas.com/climate/ghana_climate.html",
    "https://www.tandfonline.com/doi/full/10.1080/17565529.2014.951013#d1e143",
    "https://d1wqtxts1xzle7.cloudfront.net/50704361/CLIMATE_CHANGE_AGRICULTURE_AND_FOODCROP_20161204-7977-11g8oao-libre.pdf?1480848506=&response-content-disposition=inline%3B+filename%3DClimate_change_agriculture_and_foodcrop.pdf&Expires=1764945354&Signature=FqvPCcdQN1et9XH40IYvyQ4RApg09E3pQx0hcMqQ43HwWK0QN7Uc-qSnN-9ig5T1rU0LMZeBbDXqY48J32CDT-PTDckvtyKMhLOBg3DGAFOWV7f5nJfuYZDEKouVL7w-l2nftiwsTZGj6jNQWTnmGBrUPwjp6uB-lmcpxf9KUfXnSMuUbQTXWfOfS1KTtUbMiV9jm9qeVN4rX2xHt6iUZqDQ3woefKrW3wAYkONGJcSnO2H3w4foYZGlQzaB0~cJZ8smr75n8219EN~6EL7zeV~xENkUdRYRcEx7SEx~D2i1ALXuMC3BJTEALG~XiliTOGJU8EDluRLdXjbkUFrP0g__&Key-Pair-Id=APKAJLOHF5GGSLRBV4ZA",
    "https://www.worldtravelguide.net/guides/africa/ghana/weather-climate-geography/",
    "https://link.springer.com/article/10.1007/s10584-018-2239-6",
    "https://www.climaterealityproject.org/blog/how-climate-crisis-impacting-ghana",
    "https://www.adaptation-undp.org/sites/default/files/resources/ghana_national_climate_change_adaptation_strategy_nccas.pdf",
    "https://www.cdacollaborative.org/wp-content/uploads/2023/08/Climate-and-Conflict-in-Ghana.pdf",
    "https://www.cell.com/heliyon/fulltext/S2405-8440%2823%2902698-1",
    "https://www.researchgate.net/profile/Frank-Agyei-2/publication/305927297_Sustainability_of_Climate_Change_Adaptation_Strategies_Experiences_from_Eastern_Ghana/links/58cfd62192851c5009efb44e/Sustainability-of-Climate-Change-Adaptation-Strategies-Experiences-from-Eastern-Ghana.pdf?_sg%5B0%5D=started_experiment_milestone&origin=journalDetail",
    "https://www.tandfonline.com/doi/full/10.1080/10106049.2023.2289458#abstract",
    "https://link.springer.com/article/10.1186/s40068-021-00230-8",
    "https://journals.sagepub.com/doi/full/10.1177/14614529231200167",
    "https://onlinelibrary.wiley.com/doi/full/10.1002/sd.70132",
    "https://www.sciencedirect.com/science/article/pii/S0264837725002182",
    "https://www.sciencedirect.com/science/article/pii/S2226585618301857",
    "https://police.gov.gh/en/index.php/regional-commanders-responsibilities/",
    "https://police.gov.gh/en/index.php/domestic-violence-victims-support-unit-dovvsu/",
    "https://ghalii.org/akn/gh/act/2020/1030/eng@2020-10-06",
    "https://police.gov.gh/en/index.php/administration/",
    "https://ghanadmission.com/ghana-national-fire-service/",
    "https://ghalii.org/akn/gh/act/1996/526/eng@1996-12-31",
    "https://police.gov.gh/en/index.php/accra-region/",
    "https://gnfs.gov.gh/#",
    "https://www.ghanaweb.com/GhanaHomePage/features/Restructuring-Ghana-s-National-Security-Architecture-The-Role-of-Prosper-Bani-1967683",
    "https://police.gov.gh/en/index.php/paid-police-services/",
    "https://asetena.com/list-of-emergency-numbers-in-ghana/",
    "https://police.gov.gh/en/index.php/about-gps/",
    "https://www.afro.who.int/photo-story/basic-emergency-care-saving-lives-ghana",
    "https://ga.mil.gh/training/recruits/arts",
    "https://d1wqtxts1xzle7.cloudfront.net/87437165/108354211x1301408127036920220613-1-1o4dfct-libre.pdf?1655116874=&response-content-disposition=inline%3B+filename%3DTourism_Trends_in_Ghana_The_Accommodatio.pdf&Expires=1764937231&Signature=RJutb~rlm5FpFDd3Tuynm-3hpg3Ic8~NVRW-QptDj81OCOs4mCxkkLyN-vkP~alp8ZG9d27PghkPfHY1pTnVAf1FdEJ1rzYpYGXonz16enx275f1OlfAY8pPB61kdRpBi7DO2FEQj6HwY0Fu94wPqXPRuJKKBPzAEJxPvLJZV6hEwYjhy5UYKb1qtw17HRDc5k4qTyhOZBwj5P6i~WMmfCYlJ6bcKw1ugFX~TSSHZUEuUZraApWgc7QoGzRpl26odzY-GOqtCGDz5p7DDhjD6bdky8B3GrSfEeeO9KU9vsPIxO2gmM8JxRIoJN9nUYZW1AdoiafOq7Uq8jxGvDot4g__&Key-Pair-Id=APKAJLOHF5GGSLRBV4ZA",
    "https://d1wqtxts1xzle7.cloudfront.net/36160372/2173-6334-1-PB-libre.pdf?1420539734=&response-content-disposition=inline%3B+filename%3DTHE_IMPACT_OF_TOURISM_ON_ECONOMIC_PERFOR.pdf&Expires=1764937703&Signature=BlDRGX5eRaYyeJtBJ~dbB-GEfnIt4EpYWPlu4RbxAOjWFyXBnH-aL7gMs6TE1J6IcYZt3T5yK-0zB0YhtnPFGsnqfwMPxToM3xeP7WwqXRhNsGD2e~jNH5kOF7QhdKYszPHhgRGkJFagx~tlUvHFakzhiKx26EmxxUt1T5Rs3E~cuQ5pb5W4-ZiRb76epk1keODv0hdjDYZPQhOFDPEXsfU~bdtf8Mvk5djZnCl8vOTrAayAx5PVFzxadEhWAK2Pae-FN5s2b-CVQ7wZUnJCGGSFQut31Y86to0445R5qtHUIQYEJGigYudkcHpZJE4TjqmUfelipDeBlbtOEPURfA__&Key-Pair-Id=APKAJLOHF5GGSLRBV4ZA",
    "https://journals.sagepub.com/doi/epdf/10.1177/004728750204100109",
    "https://www.sciencedirect.com/science/article/pii/S144767701530108X",
    "https://journals.co.za/doi/epdf/10.10520/AJA08556261_68",
    "https://www.emerald.com/ihr/article/36/1/25/107192/Stakeholder-role-in-tourism-sustainability-the",
    "https://www.tandfonline.com/doi/full/10.1080/21568316.2011.591160#d1e277",
    "https://library.fes.de/pdf-files/bueros/ghana/seitenumbruch/03531.pdf",
    "https://books.google.com.gh/books?hl=en&lr=&id=BW8AptRSSAAC&oi=fnd&pg=PR5&dq=agriculture+in+ghana&ots=NFd10bb_Lc&sig=d3HRBfsvLXl0HhN6TBFnu3GNAE0&redir_esc=y#v=onepage&q=agriculture%20in%20ghana&f=false",
    "https://academicjournals.org/journal/AJAR/article-full-text-pdf/F96A14939032.pdf",
    "http://www.udsspace.uds.edu.gh/bitstream/123456789/156/1/Youth%20in%20agriculture%20Prospects%20and%20challenges%20in%20the%20Sissala%20area%20of%20Ghana.pdf",
    "https://d1wqtxts1xzle7.cloudfront.net/50704361/CLIMATE_CHANGE_AGRICULTURE_AND_FOODCROP_20161204-7977-11g8oao-libre.pdf?1480848506=&response-content-disposition=inline%3B+filename%3DClimate_change_agriculture_and_foodcrop.pdf&Expires=1764949188&Signature=fHCMh8nL2DOdNl5LoidNLqBxt95160BurPYXSpbCN6IFo9lFULJA-a8xC4e8ncq4Eeufb~xT-cgV1ucs5vmztRv2wYwjmu58n1PXdILHgxH6mfRFwht8VjPdop3OXXaMM1w3YRDAucqhwniQwT3rlmGSAiUxDWBHuazEikCgi2Kyru8uPixTqznboQXgAWwKP4tAbHs~bs3-WZZHg6AoA3gtkqeFg4je0MrTN8yggZuxPrExtwCK8nwxN5v8jpzG2u1Mg-VfmiGt8dHZiWIM2l4~bhlB8psd43wbZwK94LDp8Lie3vU2isNfMKQIE9rcoh3CoT3MN--uXCjmn-S4Mg__&Key-Pair-Id=APKAJLOHF5GGSLRBV4ZA",
    "http://www.savap.org.pk/journals/ARInt./Vol.5(4)/2014(5.4-28).pdf",
    "https://onlinelibrary.wiley.com/doi/full/10.1111/dech.12429",
    "https://www.researchgate.net/profile/Stephen-Doso-Jnr/publication/325343569_Effects_of_Loss_of_Agricultural_Land_Due_to_Large-Scale_Gold_Mining_on_Agriculture_in_Ghana_The_Case_of_the_Western_Region/links/5b06c64a0f7e9b1ed7e92fe2/Effects-of-Loss-of-Agricultural-Land-Due-to-Large-Scale-Gold-Mining-on-Agriculture-in-Ghana-The-Case-of-the-Western-Region.pdf",
    "https://www.mdpi.com/2071-1050/9/11/2090",
    "https://mofep.gov.gh/sites/default/files/pbb-estimates/2024/2024-PBB-MOE_.pdf",
    "https://www.opengovpartnership.org/members/ghana/commitments/GH0039/",
    "https://www.opengovpartnership.org/wp-content/uploads/2021/10/Ghana_Action-Plan_2021-2023_Revised.pdf",
    "https://www.opengovpartnership.org/wp-content/uploads/2021/10/Ghana_Action-Plan_2021-2023.pdf",
    "https://www.kaggle.com/datasets/citizen-ds-ghana/sona-ghana/data",
    "https://www.nyulawglobal.org/globalex/ghana1.html",
    "https://ndownloader.figshare.com/files/11102702",
    "https://www.climatewatchdata.org/countries/GHA?end_year=2022&start_year=1990",
]


#These are the PDF files in our pdf_datasets folder
pdfs_to_process = [
    "1_Abridged-version-of-Customs-Act.pdf",
    "2021-Citizens-Budget_Asante_Twi.pdf",
    "2021-Citizens-Budget_Ewe.pdf",
    "2021-Citizens-Budget_Ga.pdf",
    "2022-Citizens-Budget_Asante_Twi (1).pdf",
    "2022-Citizens-Budget_Asante_Twi.pdf",
    "2022-Citizens-Budget_Dangme.pdf",
    "2022-Citizens-Budget_English.pdf",
    "2022-Citizens-Budget_Ewe.pdf",
    "2022-Citizens-Budget_Ga.pdf",
    "2022-Citizens-Budget_Gonja.pdf",
    "2023-Citizens-Budget_Dangme.pdf",
    "2023-Citizens-Budget_Ewe.pdf",
    "2023-Citizens-Budget_Nzema.pdf",
    "2024_Annual_Report.pdf",
    "2025-Budget-Statement-and-Economic-Policy_v5.pdf",
    "2025-Budget-by-Detail_001_OGM.pdf",
    "2025-Budget-by-Detail_002_OHCS.pdf",
    "2025-Budget-by-Detail_003_PG.pdf",
    "2025-Budget-by-Detail_005_AS.pdf",
    "2025-Budget-by-Detail_006_PSC.pdf",
    "2025-Budget-by-Detail_008_EC.pdf",
    "2025-Budget-by-Detail_009_MFARI.pdf",
    "2025-Budget-by-Detail_010_MoF.pdf",
    "2025-Budget-by-Detail_013_MLNR.pdf",
    "2025-Budget-by-Detail_015_MoTI.pdf",
    "2025-Budget-by-Detail_017_MESTI.pdf",
    "2025-Budget-by-Detail_018_MOE.pdf",
    "2025-Budget-by-Detail_021_MWH.pdf",
    "2025-Budget-by-Detail_024_MELR.pdf",
    "2025-Budget-by-Detail_025_MoYS.pdf",
    "2025-Budget-by-Detail_027_NCCE.pdf",
    "2025-Budget-by-Detail_032_MGCSP.pdf",
    "2025-Budget-by-Detail_039_NDPC.pdf",
    "2025-Budget-by-Detail_041_NLC.pdf",
    "2025-Budget-by-Detail_084_MoYD.pdf",
    "2025-Citizens-Budget.pdf",
    "2025-Mid-Year-Fiscal-Policy-Review.pdf",
    "2026-Budget-Statement-and-Economic-Policy.pdf",
    "4_Abridged-version-of-Income-Tax-Act.pdf",
    "BANKS AND SPECIAL DEPOSIT  ACT, 2016.pdf",
    "Communications-Service-Tax-Amendment.-Act-2013..pdf",
    "Covid-19 Health Recovery Levy Act.pdf",
    "EXEMPTIONS BILL, 2019.pdf",
    "Education  Regulation Bodies Bill, 2019.pdf",
    "Electronic-Transfer-Levy-Act-2022-Act-1075.pdf",
    "Energy Sector Levies (Amendment) Act.pdf",
    "GHANA EDUCATION TRUST FUND (AMENDMENT) BILL, 2025_0001.pdf",
    "GHANA SCHOLARSHIPS AUTHORITY BILL, 2025.pdf",
    "GROWTH AND SUSTAINABILITY (AMENDMENT) BILL, 2025_0001.pdf",
    "GSE-MONTHLY-SUMMARY-MAY-2025.pdf",
    "GSE-MONTHLY-SUMMARY-OCTOBER2025.pdf",
    "Ghana National Research Fund Bill.pdf",
    "Ghana-Act-967-Standard-for-Automatic.pdf",
    "INCOME-TAX-ACT-2015-ACT-896.pdf",
    "OPAPlan.pdf",
    "POLICE SERVICE ACT.pdf",
    "Police Service (Amendment) Regulations 2020.pdf",
    "Police Service Act 1965.pdf",
    "Police Service Regulations 2012.pdf",
    "Report.pdf",
    "SECURITY AND INTELLIGENCE AGENCIES ACT.pdf",
    "Standard-for-Automatic-Exchange-of-Financial-Account-Information-Amendment-Act-2023-Act-1099.pdf",
    "VALUE ADDED TAX (AMENDMENT) (NO. 2) ACT, 2017.pdf",
    "gra_act.pdf",
]


def populate_database():
    
    print("\nStarting Database Population Process\n")

    print("Initializing ChromaDB")

    # We used PersistentClient to make sure that our data is stored on the disk for persistent access.
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # From our tests we found the best embedding function as multi-qa-MiniLM-L6-dot-v1 and decided to use it for our database.
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="multi-qa-MiniLM-L6-dot-v1"
    )

    try:
        # We tried to get existing collection
        collection = client.get_collection(name="Ghana_chatbot")
        
        # We checked if the collection has the right embedding function
        try:
            # We tested compatibility with a small query
            test_result = collection.query(query_texts=["test"], n_results=1)
        except Exception as e:
            # If incompatible, we deleted and recreated the collection
            client.delete_collection(name="Ghana_chatbot")
            collection = client.create_collection(
                name="Ghana_chatbot",
                metadata={"description": "A collection of documents about Ghana."},
                embedding_function=sentence_transformer_ef
            )
            
    except Exception as e:
        # We created a new collection if one didn't exist
        collection = client.create_collection(
            name="Ghana_chatbot",
            metadata={"description": "A collection of documents about Ghana."},
            embedding_function=sentence_transformer_ef
        )

    # We then process all our URLs using the utility function we designed in chroma_utilities.py
    print("\nProcessing URLs using scrape_multiple_urls_to_database...\n")
    
    scrape_multiple_urls_to_database(urls_to_scrape, collection)
    
    print("\nURL Processing Complete!")

    # After the scrapping, we processed the PDF files from pdf_datasets folder
    print("\nStarting PDF Dataset Processing\n")
    print(f"Processing {len(pdfs_to_process)} PDF files\n")

    for idx, pdf_file in enumerate(pdfs_to_process, 1):
        print(f"[{idx}/{len(pdfs_to_process)}] Processing: {pdf_file}")

        # Build the full path to the PDF file
        pdf_path = PDF_DATASETS_PATH + "/" + pdf_file

        # Add the PDF to the database using our utility function
        pdf_to_database(pdf_path, collection)

        

    print(f"\nSuccessfully processed {len(pdfs_to_process)} PDF files")

    print("\n\nDatabase Population Complete!")



populate_database()
