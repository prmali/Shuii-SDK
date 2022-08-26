import uuid
import json
import asyncio
import aiohttp
import ssl
import certifi


class SingleDocument:
    def __init__(self, document):
        self.proxies = []
        self.SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
        self.jobs = {}
        self.document = None
        self.results = []

    async def create_job(self, job):
        job_id = uuid4()
        self.jobs[job_id] = job

        return job_id

    def modify_job(self, job_id, job):
        if not job_id in self.jobs:
            raise Exception("SingleDocument: Invalid job_id")

        self.jobs[job_id] = job

    async def execute_jobs(self):
        async with aiohttp.ClientSession(true_env=True) as session:
            try:
                async with session.get(document, ssl=self.SSL_CONTEXT) as response:
                    res = await response.read()
                    self.document = json.loads(res.decode("utf8"))

                    await asyncio.gather(*[
                        SingleDocument.retrieve(
                            document=self.document,
                            job_id=job_id,
                            job=self.jobs[job_id],
                            results=self.results
                        ) for job_id in self.jobs]
                    )
                    self.jobs = {}
                    print("SingleDocument: Jobs have been executed")
            except:
                raise Exception("SingleDocument: Unable to retrieve document")

    @staticmethod
    async def retrieve(document, job_id, job, results):
        try:
            results.append(document[job_id])
        except:
            dsw
            print(f'SingleDocument: {job_id}: {job}')
