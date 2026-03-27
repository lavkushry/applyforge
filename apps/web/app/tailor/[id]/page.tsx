'use client'
import { useParams } from 'next/navigation'
import { useState } from 'react'
import { api } from '@/lib/api'
export default function TailorPage(){const {id}=useParams<{id:string}>(); const [data,setData]=useState<any>(null); return <section className='card space-y-3'><h2 className='text-xl font-semibold'>Tailored Resume</h2><button className='rounded bg-indigo-600 px-3 py-2' onClick={async()=>setData(await api(`/jobs/${id}/tailor`,{method:'POST'}))}>Generate Tailored Version</button><pre className='rounded bg-slate-950 p-3 text-xs'>{JSON.stringify(data,null,2)}</pre></section>}
