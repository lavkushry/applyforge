'use client'
import { useParams } from 'next/navigation'
import { useState } from 'react'
import { api } from '@/lib/api'
export default function ScoreDetail(){const {id}=useParams<{id:string}>(); const [score,setScore]=useState<any>(null); return <section className='card space-y-3'><h2 className='text-xl font-semibold'>Match Score Detail</h2><button className='rounded bg-blue-600 px-3 py-2' onClick={async()=>setScore(await api(`/jobs/${id}/score`,{method:'POST'}))}>Refresh Score</button><pre className='rounded bg-slate-950 p-3 text-xs'>{JSON.stringify(score,null,2)}</pre></section>}
