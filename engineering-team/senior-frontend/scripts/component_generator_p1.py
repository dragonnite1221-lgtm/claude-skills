# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from component_generator_base import *  # noqa: F403,E402


TEMPLATES = {
    "client": '''\'use client\';

import {{ useState }} from 'react';
import {{ cn }} from '@/lib/utils';

interface {name}Props {{
  className?: string;
  children?: React.ReactNode;
}}

export function {name}({{ className, children }}: {name}Props) {{
  return (
    <div className={{cn('', className)}}>
      {{children}}
    </div>
  );
}}
''',

    "server": '''import {{ cn }} from '@/lib/utils';

interface {name}Props {{
  className?: string;
  children?: React.ReactNode;
}}

export async function {name}({{ className, children }}: {name}Props) {{
  return (
    <div className={{cn('', className)}}>
      {{children}}
    </div>
  );
}}
''',

    "hook": '''import {{ useState, useEffect, useCallback }} from 'react';

interface Use{name}Options {{
  // Add options here
}}

interface Use{name}Return {{
  // Add return type here
  isLoading: boolean;
  error: Error | null;
}}

export function use{name}(options: Use{name}Options = {{}}): Use{name}Return {{
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {{
    // Effect logic here
  }}, []);

  return {{
    isLoading,
    error,
  }};
}}
''',

    "test": '''import {{ render, screen }} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {{ {name} }} from './{name}';

describe('{name}', () => {{
  it('renders correctly', () => {{
    render(<{name}>Test content</{name}>);
    expect(screen.getByText('Test content')).toBeInTheDocument();
  }});

  it('applies custom className', () => {{
    render(<{name} className="custom-class">Content</{name}>);
    expect(screen.getByText('Content').parentElement).toHaveClass('custom-class');
  }});

  // Add more tests here
}});
''',

    "story": '''import type {{ Meta, StoryObj }} from '@storybook/react';
import {{ {name} }} from './{name}';

const meta: Meta<typeof {name}> = {{
  title: 'Components/{name}',
  component: {name},
  tags: ['autodocs'],
  argTypes: {{
    className: {{
      control: 'text',
      description: 'Additional CSS classes',
    }},
  }},
}};

export default meta;
type Story = StoryObj<typeof {name}>;

export const Default: Story = {{
  args: {{
    children: 'Default content',
  }},
}};

export const WithCustomClass: Story = {{
  args: {{
    className: 'bg-blue-100 p-4',
    children: 'Styled content',
  }},
}};
''',

    "index": '''export {{ {name} }} from './{name}';
export type {{ {name}Props }} from './{name}';
''',
}
def to_pascal_case(name: str) -> str:
    """Convert string to PascalCase."""
    # Handle kebab-case and snake_case
    words = name.replace('-', '_').split('_')
    return ''.join(word.capitalize() for word in words)
