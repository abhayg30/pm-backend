from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from industry.models import JobDescription
from django.db.models import F, ExpressionWrapper, fields
import logging
import boto3
import PyPDF2
import io
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
from application.models import MatchedJobs
from student.resume.models import UploadResume
from django.conf import settings
import numpy as np
s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)

logger = logging.getLogger("django")


def matchingProjects(*args, **options):
    """generating recommendations for each user
    """
    logger.info("cron2 was called")
    recommendations = defaultdict(list)
    try:
        user_resumes = getAllResumes()
        if user_resumes != None:
            all_jobs = JobDescription.objects.all().order_by("-created_at")
            for instance in user_resumes:
                job_ids, score_list = [], []
                user_data = getResumeText(str(instance.resume))
                for job in all_jobs:
                    description = job.description
                    job_ids.append(job.id)
                    score_list.append(score(description, user_data))
                recommendations[instance.user_id] = sort_list(job_ids, score_list)
            bulk_insert_data(recommendations)
            logger.info("Bulk insertion successfully")
    except Exception as e:
        logger.error("Error occurred", str(e))

#Util function for bulk insertion
def bulk_insert_data(data_dict):
    MatchedJobs.objects.all().delete()
    objects_to_insert = [
        MatchedJobs(user_id=int(key), job_id=value) for key, value in data_dict.items()
    ]

    MatchedJobs.objects.bulk_create(objects_to_insert)

#util function to clean resume
def cleanResume(resumeText):
    resumeText = re.sub("http\S+\s", " ", resumeText)
    resumeText = re.sub("RT|cc", " ", resumeText)
    resumeText = re.sub("#\S+", " ", resumeText)
    resumeText = re.sub("@\S+", "  ", resumeText)
    resumeText = re.sub(
        "[%s]" % re.escape("""!"#$%&'()+,-./:;<=>?@[]^_`{|}~"""), " ", resumeText
    )
    resumeText = re.sub(r"[^\x00-\x7f]", r" ", resumeText)
    resumeText = re.sub("\s+", " ", resumeText)
    return resumeText

#fucntion to calculate similarity score
def score(text1, text2):
    text1 = cleanResume(text1)
    text2 = cleanResume(text2)

    vectorizer = TfidfVectorizer()
    matrixpol1 = vectorizer.fit_transform([text1])
    matrixpol2 = vectorizer.transform([text2])
    return cosine_similarity(matrixpol1, matrixpol2)[0][0]

#Get all resumes
def getAllResumes():
    try:
        resumes = UploadResume.objects.all()
        return resumes
    except:
        pass

#Extract text out of the resume
def getResumeText(resume):
    response = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=str(resume))
    pdf_content = response["Body"].read()

    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))

    text_content = ""
    for page_num in range(len(pdf_reader.pages)):
        text_content += pdf_reader.pages[page_num].extract_text()
    text_content = cleanResume(text_content)
    return text_content


def sort_list(list1, list2):
    idx = np.argsort(list2)
    return list(np.array(list1)[idx])[::-1]
