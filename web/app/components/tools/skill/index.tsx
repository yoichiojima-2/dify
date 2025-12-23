'use client'
import type { SkillProvider } from '@/service/use-tools'
import { useMemo, useState } from 'react'
import { useSkillProviders } from '@/service/use-tools'
import { cn } from '@/utils/classnames'
import NewSkillCard from './create-card'
import SkillDetailPanel from './detail/provider-detail'
import SkillCard from './provider-card'

type Props = {
  searchText: string
}

function renderDefaultCard() {
  const defaultCards = Array.from({ length: 36 }, (_, index) => (
    <div
      key={index}
      className={cn(
        'inline-flex h-[111px] rounded-xl bg-background-default-lighter opacity-10',
        index < 4 && 'opacity-60',
        index >= 4 && index < 8 && 'opacity-50',
        index >= 8 && index < 12 && 'opacity-40',
        index >= 12 && index < 16 && 'opacity-30',
        index >= 16 && index < 20 && 'opacity-25',
        index >= 20 && index < 24 && 'opacity-20',
      )}
    >
    </div>
  ))
  return defaultCards
}

const SkillList = ({
  searchText,
}: Props) => {
  const { data: list = [] as SkillProvider[], refetch } = useSkillProviders()

  const filteredList = useMemo(() => {
    return list.filter((provider) => {
      if (searchText) {
        return provider.name.toLowerCase().includes(searchText.toLowerCase())
          || provider.skill_identifier.toLowerCase().includes(searchText.toLowerCase())
      }
      return true
    })
  }, [list, searchText])

  const [currentProviderID, setCurrentProviderID] = useState<string>()

  const currentProvider = useMemo(() => {
    return list.find(provider => provider.id === currentProviderID)
  }, [list, currentProviderID])

  const handleCreate = async (provider: SkillProvider) => {
    await refetch()
    setCurrentProviderID(provider.id)
  }

  return (
    <>
      <div
        className={cn(
          'relative grid shrink-0 grid-cols-1 content-start gap-4 px-12 pb-4 pt-2 sm:grid-cols-1 md:grid-cols-2 xl:grid-cols-4 2xl:grid-cols-5 2k:grid-cols-6',
          !list.length && 'h-[calc(100vh_-_136px)] overflow-hidden',
        )}
      >
        <NewSkillCard handleCreate={handleCreate} />
        {filteredList.map(provider => (
          <SkillCard
            key={provider.id}
            data={provider}
            currentProvider={currentProvider}
            handleSelect={setCurrentProviderID}
            onDeleted={refetch}
          />
        ))}
        {!list.length && renderDefaultCard()}
      </div>
      {currentProvider && (
        <SkillDetailPanel
          detail={currentProvider}
          onHide={() => setCurrentProviderID(undefined)}
        />
      )}
    </>
  )
}
export default SkillList
