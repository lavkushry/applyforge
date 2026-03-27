'use client'
import Link from 'next/link'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
export default function ApplicationsBoard(){const [apps,setApps]=useState<any[]>([]); useEffect(()=>{api<any[]>('/applications').then(setApps)},[]); return <section className='space-y-3'><h2 className='card text-xl font-semibold'>Applications Tracker</h2><div className='grid gap-2'>{apps.map((a)=><div key={a.id} className='card flex items-center justify-between'><div><p className='font-semibold'>Application #{a.id}</p><p className='text-slate-400'>{a.status}</p></div><Link href={`/runs/${a.id}`} className='rounded border border-slate-600 px-3 py-2'>View Run</Link></div>)}</div></section>}
