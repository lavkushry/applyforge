'use client'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
export default function Dashboard(){const [jobs,setJobs]=useState<any[]>([]); const [apps,setApps]=useState<any[]>([]); useEffect(()=>{api<any[]>('/jobs').then(setJobs).catch(()=>{}); api<any[]>('/applications').then(setApps).catch(()=>{})},[]); return <section className='grid gap-4 md:grid-cols-3'><div className='card'><p className='text-slate-400'>Jobs</p><p className='text-4xl font-bold'>{jobs.length}</p></div><div className='card'><p className='text-slate-400'>Applications</p><p className='text-4xl font-bold'>{apps.length}</p></div><div className='card'><p className='text-slate-400'>Automation Readiness</p><p className='text-2xl font-semibold'>Human-in-the-loop enabled</p></div></section>}
