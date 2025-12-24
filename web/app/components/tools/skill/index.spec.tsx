import type { SkillProvider } from '@/service/use-tools'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

// Import components after mocks
import NewSkillCard from './create-card'
import SkillList from './index'
import SkillModal from './modal'
import SkillCard from './provider-card'

// Mock service hooks
const mockSkillProviders: SkillProvider[] = []
const mockRefetch = vi.fn()
const mockDeleteSkill = vi.fn()
const mockInstallSkill = vi.fn()
const mockUploadSkill = vi.fn()
const mockInvalidateSkillProviders = vi.fn()

vi.mock('@/service/use-tools', () => ({
  useSkillProviders: () => ({
    data: mockSkillProviders,
    refetch: mockRefetch,
  }),
  useSkillProviderDetail: (id: string) => ({
    data: mockSkillProviders.find(p => p.id === id),
    isLoading: false,
  }),
  useDeleteSkill: () => ({
    mutateAsync: mockDeleteSkill,
  }),
  useInstallSkill: () => ({
    mutateAsync: mockInstallSkill,
  }),
  useUploadSkill: () => ({
    mutateAsync: mockUploadSkill,
  }),
  useInvalidateSkillProviders: () => mockInvalidateSkillProviders,
}))

// Mock context
let mockIsWorkspaceManager = true
vi.mock('@/context/app-context', () => ({
  useAppContext: () => ({
    isCurrentWorkspaceManager: mockIsWorkspaceManager,
  }),
}))

// Factory function for creating skill provider test data
const createSkillProvider = (overrides: Partial<SkillProvider> = {}): SkillProvider => ({
  id: 'skill-1',
  name: 'Test Skill',
  skill_identifier: 'test-skill',
  description: 'A test skill for unit testing',
  icon: { background: '#6366f1', content: '🎯' },
  source_type: 'git',
  source_url: 'https://github.com/test/skill',
  version: '1.0.0',
  author: 'Test Author',
  has_scripts: true,
  enabled: true,
  created_at: '2024-01-01T00:00:00Z',
  ...overrides,
})

describe('SkillCard', () => {
  const mockHandleSelect = vi.fn()
  const mockOnDeleted = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    mockIsWorkspaceManager = true
  })

  // Basic rendering tests
  describe('Rendering', () => {
    it('should render skill name and identifier', () => {
      const skill = createSkillProvider()
      render(
        <SkillCard
          data={skill}
          handleSelect={mockHandleSelect}
          onDeleted={mockOnDeleted}
        />,
      )

      expect(screen.getByText('Test Skill')).toBeInTheDocument()
      expect(screen.getByText('test-skill')).toBeInTheDocument()
    })

    it('should render version number', () => {
      const skill = createSkillProvider({ version: '2.0.0' })
      render(
        <SkillCard
          data={skill}
          handleSelect={mockHandleSelect}
          onDeleted={mockOnDeleted}
        />,
      )

      expect(screen.getByText('v2.0.0')).toBeInTheDocument()
    })

    it('should show scripts indicator when has_scripts is true', () => {
      const skill = createSkillProvider({ has_scripts: true })
      render(
        <SkillCard
          data={skill}
          handleSelect={mockHandleSelect}
          onDeleted={mockOnDeleted}
        />,
      )

      expect(screen.getByText('tools.skill.hasScripts')).toBeInTheDocument()
    })

    it('should show no scripts indicator when has_scripts is false', () => {
      const skill = createSkillProvider({ has_scripts: false })
      render(
        <SkillCard
          data={skill}
          handleSelect={mockHandleSelect}
          onDeleted={mockOnDeleted}
        />,
      )

      expect(screen.getByText('tools.skill.noScripts')).toBeInTheDocument()
    })

    it('should show disabled badge when enabled is false', () => {
      const skill = createSkillProvider({ enabled: false })
      render(
        <SkillCard
          data={skill}
          handleSelect={mockHandleSelect}
          onDeleted={mockOnDeleted}
        />,
      )

      expect(screen.getByText('tools.skill.disabled')).toBeInTheDocument()
    })

    it('should highlight card when selected', () => {
      const skill = createSkillProvider()
      const { container } = render(
        <SkillCard
          data={skill}
          currentProvider={skill}
          handleSelect={mockHandleSelect}
          onDeleted={mockOnDeleted}
        />,
      )

      const card = container.firstChild as HTMLElement
      expect(card.className).toContain('border-components-option-card-option-selected-border')
    })
  })

  // User interaction tests
  describe('User Interactions', () => {
    it('should call handleSelect when card is clicked', async () => {
      const user = userEvent.setup()
      const skill = createSkillProvider()
      render(
        <SkillCard
          data={skill}
          handleSelect={mockHandleSelect}
          onDeleted={mockOnDeleted}
        />,
      )

      await user.click(screen.getByText('Test Skill'))

      expect(mockHandleSelect).toHaveBeenCalledWith('skill-1')
    })
  })

  // Props tests
  describe('Props', () => {
    it('should handle string icon gracefully', () => {
      const skill = createSkillProvider({ icon: '🚀' })
      render(
        <SkillCard
          data={skill}
          handleSelect={mockHandleSelect}
          onDeleted={mockOnDeleted}
        />,
      )

      // Should not crash and render the name
      expect(screen.getByText('Test Skill')).toBeInTheDocument()
    })
  })
})

describe('NewSkillCard', () => {
  const mockHandleCreate = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    mockIsWorkspaceManager = true
  })

  // Rendering tests
  describe('Rendering', () => {
    it('should render add skill card for workspace managers', () => {
      render(<NewSkillCard handleCreate={mockHandleCreate} />)

      expect(screen.getByText('tools.skill.create.cardTitle')).toBeInTheDocument()
      expect(screen.getByText('tools.skill.create.cardLink')).toBeInTheDocument()
    })

    it('should not render card for non-managers', () => {
      mockIsWorkspaceManager = false
      render(<NewSkillCard handleCreate={mockHandleCreate} />)

      // Card should not render for non-managers
      expect(screen.queryByText('tools.skill.create.cardTitle')).not.toBeInTheDocument()
      expect(screen.queryByText('tools.skill.create.cardLink')).not.toBeInTheDocument()
    })
  })

  // User interaction tests
  describe('User Interactions', () => {
    it('should open modal when card is clicked', async () => {
      const user = userEvent.setup()
      render(<NewSkillCard handleCreate={mockHandleCreate} />)

      await user.click(screen.getByText('tools.skill.create.cardTitle'))

      await waitFor(() => {
        expect(screen.getByText('tools.skill.create.title')).toBeInTheDocument()
      })
    })
  })
})

describe('SkillModal', () => {
  const mockOnConfirm = vi.fn()
  const mockOnHide = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    mockInstallSkill.mockResolvedValue(createSkillProvider())
    mockUploadSkill.mockResolvedValue(createSkillProvider())
  })

  // Rendering tests
  describe('Rendering', () => {
    it('should render modal with tabs', () => {
      render(
        <SkillModal
          show
          onConfirm={mockOnConfirm}
          onHide={mockOnHide}
        />,
      )

      expect(screen.getByText('tools.skill.create.title')).toBeInTheDocument()
      expect(screen.getByText('tools.skill.create.fromGit')).toBeInTheDocument()
      expect(screen.getByText('tools.skill.create.fromUpload')).toBeInTheDocument()
    })

    it('should show Git URL input by default', () => {
      render(
        <SkillModal
          show
          onConfirm={mockOnConfirm}
          onHide={mockOnHide}
        />,
      )

      expect(screen.getByText('tools.skill.create.gitUrl')).toBeInTheDocument()
    })
  })

  // Tab switching tests
  describe('Tab Switching', () => {
    it('should switch to upload tab when clicked', async () => {
      const user = userEvent.setup()
      render(
        <SkillModal
          show
          onConfirm={mockOnConfirm}
          onHide={mockOnHide}
        />,
      )

      await user.click(screen.getByText('tools.skill.create.fromUpload'))

      await waitFor(() => {
        expect(screen.getByText('tools.skill.create.uploadFile')).toBeInTheDocument()
      })
    })
  })

  // Form validation tests
  describe('Form Validation', () => {
    it('should not call install when git URL is empty', async () => {
      const user = userEvent.setup()
      render(
        <SkillModal
          show
          onConfirm={mockOnConfirm}
          onHide={mockOnHide}
        />,
      )

      await user.click(screen.getByText('tools.skill.create.install'))

      // Install should not be called when URL is empty
      expect(mockInstallSkill).not.toHaveBeenCalled()
    })
  })

  // Submission tests
  describe('Submission', () => {
    it('should call install with git URL when submitted', async () => {
      const user = userEvent.setup()
      render(
        <SkillModal
          show
          onConfirm={mockOnConfirm}
          onHide={mockOnHide}
        />,
      )

      // Find the Git URL input by placeholder
      const gitUrlInput = screen.getByPlaceholderText('https://github.com/org/skill-repo')
      await user.type(gitUrlInput, 'https://github.com/test/skill')

      await user.click(screen.getByText('tools.skill.create.install'))

      await waitFor(() => {
        expect(mockInstallSkill).toHaveBeenCalled()
      })
    })
  })

  // Close behavior tests
  describe('Close Behavior', () => {
    it('should call onHide when cancel button is clicked', async () => {
      const user = userEvent.setup()
      render(
        <SkillModal
          show
          onConfirm={mockOnConfirm}
          onHide={mockOnHide}
        />,
      )

      // Find and click cancel button
      const cancelButton = screen.getByText('common.operation.cancel')
      await user.click(cancelButton)

      expect(mockOnHide).toHaveBeenCalled()
    })
  })
})

describe('SkillList', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockIsWorkspaceManager = true
    mockSkillProviders.length = 0
  })

  // Rendering tests
  describe('Rendering', () => {
    it('should render empty state when no skills', () => {
      render(<SkillList searchText="" />)

      // Should show the create card and placeholder cards
      expect(screen.getByText('tools.skill.create.cardTitle')).toBeInTheDocument()
    })

    it('should render skill cards when skills exist', () => {
      mockSkillProviders.push(
        createSkillProvider({ id: 'skill-1', name: 'Skill One' }),
        createSkillProvider({ id: 'skill-2', name: 'Skill Two' }),
      )

      render(<SkillList searchText="" />)

      expect(screen.getByText('Skill One')).toBeInTheDocument()
      expect(screen.getByText('Skill Two')).toBeInTheDocument()
    })
  })

  // Filtering tests
  describe('Filtering', () => {
    it('should filter skills by search text', () => {
      mockSkillProviders.push(
        createSkillProvider({ id: 'skill-1', name: 'Alpha Skill', skill_identifier: 'alpha' }),
        createSkillProvider({ id: 'skill-2', name: 'Beta Skill', skill_identifier: 'beta' }),
      )

      render(<SkillList searchText="alpha" />)

      expect(screen.getByText('Alpha Skill')).toBeInTheDocument()
      expect(screen.queryByText('Beta Skill')).not.toBeInTheDocument()
    })

    it('should filter by skill identifier', () => {
      mockSkillProviders.push(
        createSkillProvider({ id: 'skill-1', name: 'My Skill', skill_identifier: 'unique-id' }),
        createSkillProvider({ id: 'skill-2', name: 'Other Skill', skill_identifier: 'other' }),
      )

      render(<SkillList searchText="unique" />)

      expect(screen.getByText('My Skill')).toBeInTheDocument()
      expect(screen.queryByText('Other Skill')).not.toBeInTheDocument()
    })

    it('should show all skills when search is empty', () => {
      mockSkillProviders.push(
        createSkillProvider({ id: 'skill-1', name: 'First' }),
        createSkillProvider({ id: 'skill-2', name: 'Second' }),
      )

      render(<SkillList searchText="" />)

      expect(screen.getByText('First')).toBeInTheDocument()
      expect(screen.getByText('Second')).toBeInTheDocument()
    })
  })

  // Selection tests
  describe('Selection', () => {
    it('should show detail panel when skill is selected', async () => {
      const user = userEvent.setup()
      const skill = createSkillProvider()
      mockSkillProviders.push(skill)

      render(<SkillList searchText="" />)

      await user.click(screen.getByText('Test Skill'))

      await waitFor(() => {
        // Detail panel should appear with the skill name
        expect(screen.getAllByText('Test Skill').length).toBeGreaterThan(1)
      })
    })
  })
})

describe('Edge Cases', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockSkillProviders.length = 0
  })

  it('should handle skill with no icon', () => {
    const skill = createSkillProvider({ icon: undefined })
    render(
      <SkillCard
        data={skill}
        handleSelect={vi.fn()}
        onDeleted={vi.fn()}
      />,
    )

    expect(screen.getByText('Test Skill')).toBeInTheDocument()
  })

  it('should handle skill with no description', () => {
    const skill = createSkillProvider({ description: '' })
    mockSkillProviders.push(skill)

    render(<SkillList searchText="" />)

    expect(screen.getByText('Test Skill')).toBeInTheDocument()
  })

  it('should handle case-insensitive search', () => {
    mockSkillProviders.push(
      createSkillProvider({ name: 'UPPERCASE SKILL' }),
    )

    render(<SkillList searchText="uppercase" />)

    expect(screen.getByText('UPPERCASE SKILL')).toBeInTheDocument()
  })
})
