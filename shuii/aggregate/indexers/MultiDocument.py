import uuid
import json
import asyncio
import aiohttp
import ssl
import certifi


class MultiDocument:
    def __init__(self, retry_limit):
        self.proxies = []
        self.SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
        self.jobs = {}
        self.session = None
        self.results = {}
        self.retry_limit = retry_limit

    async def create_job(self, job_id, job):
        self.jobs[job_id] = job

    def modify_job(self, job_id, job):
        if not job_id in self.jobs:
            raise Exception("MultiDocument: Invalid job_id")

        self.jobs[job_id] = job

    async def execute_jobs(self):
        async with aiohttp.ClientSession(trust_env=True) as session:
            self.session = session
            await asyncio.gather(*[
                MultiDocument.retrieve(
                    session=self.session,
                    ssl=self.SSL_CONTEXT,
                    job_id=job_id,
                    job=self.jobs[job_id],
                    retry_limit=self.retry_limit,
                    results=self.results
                ) for job_id in self.jobs]
            )
            self.jobs = {}
            print("MultiDocument: Jobs have been executed")

    @staticmethod
    async def retrieve(session, ssl, job_id, job, retry_limit, results):
        for attempt in range(retry_limit):
            try:
                async with session.get(job, ssl=ssl) as response:
                    if not response.status == 200:
                        raise Exception("")

                    res = await response.read()
                    decoded_res = json.loads(res.decode("utf8"))
                    results[job_id] = decoded_res
                    return
            except:
                continue

        print(f'MultiDocument Retrieval Error: {job_id} - {job}')
