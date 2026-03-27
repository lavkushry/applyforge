'use client'
import { useParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
export default function RunViewPage(){const {id}=useParams<{id:string}>(); const [data,setData]=useState<any>(null); useEffect(()=>{api(`/application-runs/${id}`).then(setData)},[id]); return <section className='card'><h2 className='text-xl font-semibold'>Application Run Timeline</h2><pre className='mt-2 rounded bg-slate-950 p-3 text-xs'>{JSON.stringify(data,null,2)}</pre></section>}
