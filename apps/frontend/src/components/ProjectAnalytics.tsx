import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { formatChartDate } from '@/lib/utils';

interface ProjectAnalyticsProps {
  engagementTrendData: Array<{ date: string; engagement: number; reach: number; impressions: number }>;
  topPerformingCreators: Array<{ username: string; posts: number; avg_engagement: number; total_reach: number }>;
  reachData: Array<{ date: string; organic: number; paid: number }>;
}

export function ProjectAnalytics({
  engagementTrendData,
  topPerformingCreators,
  reachData,
}: ProjectAnalyticsProps) {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2">
        <Card className="bg-card border-border shadow-lg">
          <CardHeader>
            <CardTitle className="text-white">Engagement Trends</CardTitle>
            <CardDescription className="text-gray-400">
              Daily engagement rate over time
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={engagementTrendData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-gray-700" />
                <XAxis
                  dataKey="date"
                  tickFormatter={(value) => formatChartDate(value)}
                  className="text-gray-400"
                />
                <YAxis className="text-gray-400" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '6px',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="engagement"
                  stroke="hsl(var(--primary))"
                  fill="hsl(var(--primary))"
                  fillOpacity={0.2}
                  name="Engagement Rate (%)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="bg-card border-border shadow-lg">
          <CardHeader>
            <CardTitle className="text-white">Top Performing Creators</CardTitle>
            <CardDescription className="text-gray-400">
              By average engagement rate
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={topPerformingCreators} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" className="stroke-gray-700" />
                <XAxis type="number" className="text-gray-400" />
                <YAxis dataKey="username" type="category" width={100} className="text-gray-400" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '6px',
                  }}
                />
                <Bar dataKey="avg_engagement" fill="hsl(var(--accent))" name="Avg Engagement (%)" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card className="bg-card border-border shadow-lg">
        <CardHeader>
          <CardTitle className="text-white">Reach & Impressions</CardTitle>
          <CardDescription className="text-gray-400">
            Organic vs Paid reach over time
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={reachData}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-gray-700" />
              <XAxis
                dataKey="date"
                tickFormatter={(value) => formatChartDate(value)}
                className="text-gray-400"
              />
              <YAxis className="text-gray-400" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '6px',
                }}
              />
              <Legend />
              <Area
                type="monotone"
                dataKey="organic"
                stackId="1"
                stroke="hsl(var(--primary))"
                fill="hsl(var(--primary))"
                fillOpacity={0.8}
                name="Organic Reach"
              />
              <Area
                type="monotone"
                dataKey="paid"
                stackId="1"
                stroke="hsl(var(--accent))"
                fill="hsl(var(--accent))"
                fillOpacity={0.8}
                name="Paid Reach"
              />
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}


