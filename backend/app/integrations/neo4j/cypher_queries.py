CLEAR_DEMO_GRAPH = """
MATCH (n:IFCRDemo)
DETACH DELETE n
"""

CREATE_CONSTRAINTS = [
    "CREATE CONSTRAINT ifcr_farmer_id IF NOT EXISTS FOR (n:Farmer) REQUIRE n.farmer_id IS UNIQUE",
    "CREATE CONSTRAINT ifcr_county_id IF NOT EXISTS FOR (n:County) REQUIRE n.county_id IS UNIQUE",
    "CREATE CONSTRAINT ifcr_crop_id IF NOT EXISTS FOR (n:Crop) REQUIRE n.crop_id IS UNIQUE",
    "CREATE CONSTRAINT ifcr_cooperative_id IF NOT EXISTS FOR (n:Cooperative) REQUIRE n.cooperative_id IS UNIQUE",
    "CREATE CONSTRAINT ifcr_savings_group_id IF NOT EXISTS FOR (n:SavingsGroup) REQUIRE n.savings_group_id IS UNIQUE",
    "CREATE CONSTRAINT ifcr_buyer_id IF NOT EXISTS FOR (n:Buyer) REQUIRE n.buyer_id IS UNIQUE",
    "CREATE CONSTRAINT ifcr_supplier_id IF NOT EXISTS FOR (n:InputSupplier) REQUIRE n.supplier_id IS UNIQUE",
    "CREATE CONSTRAINT ifcr_extension_id IF NOT EXISTS FOR (n:ExtensionOfficer) REQUIRE n.extension_id IS UNIQUE",
]

UPSERT_FARMER = """
MERGE (f:IFCRDemo:Farmer {farmer_id: $farmer_id})
SET
    f.name = $name,
    f.county = $county,
    f.area = $area,
    f.crop = $crop,
    f.crop_stage = $crop_stage,
    f.season = $season,
    f.loan_request = $loan_request,
    f.loan_purpose = $loan_purpose,
    f.farmer_type = $farmer_type,
    f.preferred_channel = $preferred_channel,
    f.preferred_language = $preferred_language,
    f.phone_type = $phone_type,
    f.has_land_title = $has_land_title,
    f.mobile_money_consistency = $mobile_money_consistency,
    f.peer_lending_reliability = $peer_lending_reliability,
    f.savings_group_reliability = $savings_group_reliability,
    f.cooperative_reliability = $cooperative_reliability,
    f.buyer_payment_reliability = $buyer_payment_reliability,
    f.market_payment_consistency = $market_payment_consistency,
    f.input_purchase_frequency = $input_purchase_frequency,
    f.climate_risk_level = $climate_risk_level,
    f.pest_risk_level = $pest_risk_level,
    f.market_delay_risk = $market_delay_risk,
    f.localized_drought_exposure = $localized_drought_exposure,
    f.localized_pest_outbreak = $localized_pest_outbreak
RETURN f.farmer_id AS farmer_id
"""

LINK_COUNTY = """
MATCH (f:IFCRDemo:Farmer {farmer_id: $farmer_id})
MERGE (c:IFCRDemo:County {county_id: $county_id})
SET c.name = $county
MERGE (f)-[r:LOCATED_IN]->(c)
SET r.business_use = "geographic risk context"
RETURN f.farmer_id AS farmer_id, c.name AS county
"""

LINK_CROP = """
MATCH (f:IFCRDemo:Farmer {farmer_id: $farmer_id})
MERGE (c:IFCRDemo:Crop {crop_id: $crop_id})
SET c.name = $crop
MERGE (f)-[r:GROWS]->(c)
SET
    r.crop_stage = $crop_stage,
    r.season = $season,
    r.business_use = "seasonal crop risk context"
RETURN f.farmer_id AS farmer_id, c.name AS crop
"""

LINK_COOPERATIVE = """
MATCH (f:IFCRDemo:Farmer {farmer_id: $farmer_id})
MERGE (c:IFCRDemo:Cooperative {cooperative_id: $cooperative_id})
SET
    c.name = $cooperative_name,
    c.county = $county,
    c.crop_focus = $crop
MERGE (f)-[r:MEMBER_OF]->(c)
SET
    r.reliability = $cooperative_reliability,
    r.repayment_score = $cooperative_repayment_score,
    r.business_use = "cooperative contribution and repayment verification"
RETURN f.farmer_id AS farmer_id, c.name AS cooperative
"""

LINK_SAVINGS_GROUP = """
MATCH (f:IFCRDemo:Farmer {farmer_id: $farmer_id})
MERGE (s:IFCRDemo:SavingsGroup {savings_group_id: $savings_group_id})
SET
    s.name = $savings_group_name,
    s.area = $area,
    s.county = $county
MERGE (f)-[r:SAVES_WITH]->(s)
SET
    r.reliability = $savings_group_reliability,
    r.business_use = "group savings and social repayment evidence"
RETURN f.farmer_id AS farmer_id, s.name AS savings_group
"""

LINK_BUYER = """
MATCH (f:IFCRDemo:Farmer {farmer_id: $farmer_id})
MERGE (b:IFCRDemo:Buyer {buyer_id: $buyer_id})
SET
    b.name = $buyer_name,
    b.county = $county,
    b.crop_focus = $crop
MERGE (f)-[r:SELLS_TO]->(b)
SET
    r.payment_reliability = $buyer_payment_reliability,
    r.market_payment_consistency = $market_payment_consistency,
    r.business_use = "buyer receipt and market payment verification"
RETURN f.farmer_id AS farmer_id, b.name AS buyer
"""

LINK_INPUT_SUPPLIER = """
MATCH (f:IFCRDemo:Farmer {farmer_id: $farmer_id})
MERGE (s:IFCRDemo:InputSupplier {supplier_id: $supplier_id})
SET
    s.name = $supplier_name,
    s.county = $county
MERGE (f)-[r:BUYS_FROM]->(s)
SET
    r.input_purchase_frequency = $input_purchase_frequency,
    r.verified_input_purchase = $verified_input_purchase,
    r.business_use = "input purchase and farming activity verification"
RETURN f.farmer_id AS farmer_id, s.name AS supplier
"""

LINK_EXTENSION_OFFICER = """
MATCH (f:IFCRDemo:Farmer {farmer_id: $farmer_id})
MERGE (e:IFCRDemo:ExtensionOfficer {extension_id: $extension_id})
SET
    e.name = $extension_name,
    e.area = $area,
    e.county = $county
MERGE (f)-[r:ADVISED_BY]->(e)
SET
    r.extension_support = $extension_support,
    r.business_use = "agronomy or extension support verification"
RETURN f.farmer_id AS farmer_id, e.name AS extension_officer
"""

LINK_SIMILAR_FARMERS = """
MATCH (a:IFCRDemo:Farmer {farmer_id: $source_farmer_id})
MATCH (b:IFCRDemo:Farmer {farmer_id: $target_farmer_id})
MERGE (a)-[r:SIMILAR_TO]->(b)
SET
    r.similarity_score = $similarity_score,
    r.shared_reasons = $shared_reasons,
    r.business_use = "peer comparison and branch portfolio context"
RETURN a.farmer_id AS source, b.farmer_id AS target
"""

GET_FARMER_DIRECT_GRAPH = """
MATCH (f:IFCRDemo:Farmer {farmer_id: $farmer_id})
OPTIONAL MATCH (f)-[r]->(n:IFCRDemo)
WHERE type(r) <> "SIMILAR_TO"
RETURN
    f { .* } AS farmer,
    collect({
        relationship: type(r),
        relationship_properties: properties(r),
        node_labels: labels(n),
        node: n { .* }
    }) AS direct_relationships
"""

GET_FARMER_SIMILARITY_GRAPH = """
MATCH (f:IFCRDemo:Farmer {farmer_id: $farmer_id})
OPTIONAL MATCH (f)-[r:SIMILAR_TO]-(peer:IFCRDemo:Farmer)
RETURN collect({
    peer: peer { .* },
    similarity_score: r.similarity_score,
    shared_reasons: r.shared_reasons,
    business_use: r.business_use
}) AS similar_farmers
"""

GET_NETWORK_CONCENTRATION = """
MATCH (f:IFCRDemo:Farmer {farmer_id: $farmer_id})
OPTIONAL MATCH (f)-[:MEMBER_OF]->(coop:IFCRDemo:Cooperative)<-[:MEMBER_OF]-(coop_peer:IFCRDemo:Farmer)
OPTIONAL MATCH (f)-[:SAVES_WITH]->(sg:IFCRDemo:SavingsGroup)<-[:SAVES_WITH]-(sg_peer:IFCRDemo:Farmer)
OPTIONAL MATCH (f)-[:SELLS_TO]->(buyer:IFCRDemo:Buyer)<-[:SELLS_TO]-(buyer_peer:IFCRDemo:Farmer)
RETURN
    collect(DISTINCT {
        type: "cooperative",
        name: coop.name,
        connected_farmers: coop_peer.farmer_id
    }) AS cooperative_network,
    collect(DISTINCT {
        type: "savings_group",
        name: sg.name,
        connected_farmers: sg_peer.farmer_id
    }) AS savings_group_network,
    collect(DISTINCT {
        type: "buyer",
        name: buyer.name,
        connected_farmers: buyer_peer.farmer_id
    }) AS buyer_network
"""

COUNT_DEMO_GRAPH = """
MATCH (n:IFCRDemo)
RETURN labels(n) AS labels, count(n) AS count
"""