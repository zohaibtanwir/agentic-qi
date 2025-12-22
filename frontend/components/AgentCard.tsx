import Link from 'next/link';

interface AgentCardProps {
  name: string;
  description: string;
  status: 'operational' | 'down' | 'coming_soon';
  link: string;
  external?: boolean;
  features: string[];
  icon?: string;
}

const statusConfig = {
  operational: {
    label: 'Operational',
    dotColor: 'bg-[var(--success)]',
    bgColor: 'bg-green-50',
    textColor: 'text-green-700',
  },
  down: {
    label: 'Down',
    dotColor: 'bg-[var(--error)]',
    bgColor: 'bg-red-50',
    textColor: 'text-red-700',
  },
  coming_soon: {
    label: 'Coming Soon',
    dotColor: 'bg-gray-400',
    bgColor: 'bg-gray-50',
    textColor: 'text-gray-700',
  },
};

export function AgentCard({
  name,
  description,
  status,
  link,
  external = false,
  features,
}: AgentCardProps) {
  const config = statusConfig[status];

  const cardContent = (
    <div
      className="bg-white rounded-lg border border-[var(--border-default)] p-6 shadow-sm transition-all duration-200 h-full flex flex-col hover:shadow-md hover:border-[var(--accent-default)]"
    >
      {/* Header with status badge */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-xl font-semibold text-[var(--text-primary)] mb-1">
            {name}
          </h3>
          <p className="text-sm text-[var(--text-muted)]">{description}</p>
        </div>

        {/* Status Badge */}
        <div className={`px-3 py-1 rounded-full ${config.bgColor} flex items-center gap-2`}>
          <span className={`w-2 h-2 rounded-full ${config.dotColor}`} />
          <span className={`text-xs font-medium ${config.textColor}`}>
            {config.label}
          </span>
        </div>
      </div>

      {/* Features List */}
      <div className="mb-4 flex-1">
        <ul className="space-y-2">
          {features.map((feature, index) => (
            <li key={index} className="flex items-center text-sm text-[var(--text-secondary)]">
              <svg
                className="w-4 h-4 mr-2 text-[var(--accent-default)] flex-shrink-0"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
              {feature}
            </li>
          ))}
        </ul>
      </div>

      {/* Action Button */}
      <div className="pt-4 border-t border-[var(--border-light)]">
        <div className="flex items-center justify-between text-[var(--accent-default)] font-medium text-sm">
          <span>Open Agent</span>
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d={external ? "M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" : "M9 5l7 7-7 7"}
            />
          </svg>
        </div>
      </div>
    </div>
  );

  if (external) {
    return (
      <a
        href={link}
        target="_blank"
        rel="noopener noreferrer"
        className="block h-full"
      >
        {cardContent}
      </a>
    );
  }

  return <Link href={link} className="block h-full">{cardContent}</Link>;
}
