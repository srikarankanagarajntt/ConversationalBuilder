interface UploadCvResponse {
    sessionId: string;
    extractedData: { [key: string]: any };
    missingFields: string[];
    normalizedCvSchema: NormalizedCvSchema;
}

interface NormalizedCvSchema {
    sessionId: string;
    meta: Meta;
    header: Header;
    professionalSummary: string[];
    technicalSkills: TechnicalSkills;
    currentResponsibilities: string[];
    workExperience: WorkExperience[];
    personalDetails: PersonalDetails;
    declaration: Declaration;
}

interface Meta {
    templateVersion: string;
    sourceType: string;
    language: string;
    lastUpdated: string;
}

interface Header {
    fullName: string;
    portalId: string;
    headline: string;
    jobTitle: string;
    location: Location;
    contact: Contact;
    personal: Personal;
}

interface Location {
    companyName: string;
    addressLine1: string;
    addressLine2: string;
    city: string;
    postalCode: string;
    country: string;
}

interface Contact {
    phoneNumber: string;
    emailId: string;
    officialEmailId: string;
}

interface Personal {
    nationality: string;
}

interface TechnicalSkills {
    primary: Skill[];
    secondary: Skill[];
}

interface Skill {
    skillName: string;
    category: string;
    proficiency: string;
}

interface WorkExperience {
    employer: string;
    employmentPeriod: EmploymentPeriod;
    position: string;
    projectTitle: string;
    client: string;
    technology: string[];
    projectDescription: string;
    responsibilities: string[];
}

interface EmploymentPeriod {
    start: string;
    end: string;
    displayText: string;
}

interface PersonalDetails {
    languagesKnown: string[];
    permanentAddress: string;
}

interface Declaration {
    statement: string;
    place: string;
    signatureName: string;
}