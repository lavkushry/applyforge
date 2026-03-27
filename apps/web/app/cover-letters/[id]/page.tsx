'use client'
import { useParams } from 'next/navigation'
import { useState } from 'react'
import { api } from '@/lib/api'
export default function CoverLetterPage(){const {id}=useParams<{id:string}>(); const [data,setData]=useState<any>(null); return <section className='card space-y-3'><h2 className='text-xl font-semibold'>Cover Letter Editor</h2><button className='rounded bg-emerald-600 px-3 py-2' onClick={async()=>setData(await api(`/jobs/${id}/cover-letter`,{method:'POST'}))}>Generate</button><textarea className='h-72 w-full rounded bg-slate-800 p-3' value={data?.content || ''} onChange={()=>{}} /></section>}
