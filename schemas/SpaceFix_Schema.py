from pydantic import BaseModel, Field
from typing import List


# -------------------------------
# Address Model
# -------------------------------
class Address(BaseModel):
    house_no: str = ""
    street_address: str = ""
    landmark: str = ""
    area_locality: str = ""
    city: str = ""
    district: str = ""
    state: str = ""
    pincode: str = ""


# -------------------------------
# Local Reference
# -------------------------------
class LocalReference(BaseModel):
    lr_name: str = ""
    lr_address: str = ""
    lr_contact: str = ""


# -------------------------------
# MNP Details
# -------------------------------
class MNPDetails(BaseModel):
    upc_code: str = ""
    type_of_connection: str = ""
    existing_operator_name: str = ""
    upc_generation_date: str = ""
    existing_operator_area: str = ""


# -------------------------------
# MAIN SPACEFIX MODEL
# -------------------------------
class SpaceFixSchema(BaseModel):
    status: str = ""
    filename:str = ""
    logo_name: str = ""
    caf_no: str = ""
    service_type: str = ""

    customer_name: str = ""
    father_or_husband_name: str = ""
    date_of_birth: str = ""
    gender: str = ""
    nationality: str = ""
    alternate_contact_number: str = ""

    local_address: Address = Address()
    permanent_address: Address = Address()

    local_reference_details: LocalReference = LocalReference()

    mobile_number_allocated: str = ""
    iccid: str = ""
    imsi_number: str = ""

    mnp_details: MNPDetails = MNPDetails()

    declaration_by_pos: str = ""
    photos: List[str] = Field(default_factory=list)
    images_count:int = 0
    images_preview:List[str] = Field(default_factory=list)