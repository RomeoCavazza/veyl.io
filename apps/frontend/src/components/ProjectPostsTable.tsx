import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Heart, MessageCircle, ExternalLink, ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import { formatNumber, formatShortDate, formatRelativeTime } from '@/lib/utils';
import type { ProjectPost } from '@/types/project';

interface ProjectPostsTableProps {
  posts: ProjectPost[];
  selectedPlatformFilter: string | 'all';
  sortColumn: string;
  sortDirection: 'asc' | 'desc';
  onSort: (column: string) => void;
  onPostClick: (post: ProjectPost) => void;
}

export function ProjectPostsTable({
  posts,
  selectedPlatformFilter,
  sortColumn,
  sortDirection,
  onSort,
  onPostClick,
}: ProjectPostsTableProps) {
  const getSortIcon = (column: string) => {
    if (sortColumn !== column) {
      return <ArrowUpDown className="h-4 w-4 ml-1 opacity-50" />;
    }
    return sortDirection === 'asc' ? <ArrowUp className="h-4 w-4 ml-1" /> : <ArrowDown className="h-4 w-4 ml-1" />;
  };

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle>Posts ({posts.length})</CardTitle>
        <CardDescription>
          Tabular view of all posts with sorting
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[60px]">Image</TableHead>
                <TableHead>Link</TableHead>
                <TableHead 
                  className="cursor-pointer hover:bg-muted/50"
                  onClick={() => onSort('caption')}
                >
                  <div className="flex items-center">
                    Description
                    {getSortIcon('caption')}
                  </div>
                </TableHead>
                <TableHead 
                  className="cursor-pointer hover:bg-muted/50"
                  onClick={() => onSort('posted_at')}
                >
                  <div className="flex items-center">
                    Added
                    {getSortIcon('posted_at')}
                  </div>
                </TableHead>
                <TableHead 
                  className="text-right cursor-pointer hover:bg-muted/50"
                  onClick={() => onSort('like_count')}
                >
                  <div className="flex items-center justify-end">
                    Likes
                    {getSortIcon('like_count')}
                  </div>
                </TableHead>
                <TableHead 
                  className="text-right cursor-pointer hover:bg-muted/50"
                  onClick={() => onSort('comment_count')}
                >
                  <div className="flex items-center justify-end">
                    Comments
                    {getSortIcon('comment_count')}
                  </div>
                </TableHead>
                <TableHead className="text-right">Platform</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {posts.length > 0 ? (
                posts.map((post: ProjectPost) => (
                  <TableRow
                    key={post.id}
                    className="cursor-pointer hover:bg-muted/50"
                    onClick={() => onPostClick(post)}
                  >
                    <TableCell>
                      {post.permalink ? (
                        <div className="w-12 h-12 rounded overflow-hidden">
                          <iframe
                            src={`${post.permalink.replace(/\/$/, '')}/embed`}
                            className="w-full h-full border-0 pointer-events-none"
                            scrolling="no"
                          />
                        </div>
                      ) : (
                        <div className="w-12 h-12 rounded bg-muted flex items-center justify-center text-xs text-muted-foreground">
                          No img
                        </div>
                      )}
                    </TableCell>
                    <TableCell>
                      {post.permalink ? (
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 px-2"
                          asChild
                          onClick={(e) => e.stopPropagation()}
                        >
                          <a href={post.permalink} target="_blank" rel="noopener noreferrer">
                            <ExternalLink className="h-3 w-3" />
                          </a>
                        </Button>
                      ) : (
                        <span className="text-muted-foreground text-xs">-</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <p className="max-w-md line-clamp-2 text-sm">
                        {post.caption || '-'}
                      </p>
                    </TableCell>
                    <TableCell>
                      {post.posted_at || post.fetched_at ? (
                        <div className="text-sm">
                          <div>{formatShortDate(post.posted_at || post.fetched_at)}</div>
                          <div className="text-xs text-muted-foreground">
                            {formatRelativeTime(post.posted_at || post.fetched_at)}
                          </div>
                        </div>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-1">
                        <Heart className="h-4 w-4" />
                        <span>{formatNumber(post.like_count) || 0}</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-1">
                        <MessageCircle className="h-4 w-4" />
                        <span>{formatNumber(post.comment_count) || 0}</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      <Badge variant="outline">{post.platform || 'instagram'}</Badge>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                    {selectedPlatformFilter !== 'all' 
                      ? `No ${selectedPlatformFilter === 'meta' ? 'Meta' : 'TikTok'} posts yet. Add ${selectedPlatformFilter === 'meta' ? 'Instagram/Facebook' : 'TikTok'} creators or hashtags first.`
                      : 'No posts yet. Add creators or hashtags first.'}
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}

