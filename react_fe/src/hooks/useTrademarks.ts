import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { APIClient } from '../services/api';

export const useTrademarks = () => {
  const queryClient = useQueryClient();

  const { data: trademarks, isLoading, error, refetch } = useQuery({
    queryKey: ['trademarks'],
    queryFn: APIClient.getAllTrademarks,
    staleTime: 30000, // 30 seconds
  });

  const ingestMutation = useMutation({
    mutationFn: async (params: { applicationNumber?: string; wordmark?: string; className?: string }) => {
      if (params.applicationNumber) {
        return APIClient.ingestByApplicationNumber(params.applicationNumber);
      } else if (params.wordmark && params.className) {
        return APIClient.ingestByWordmarkAndClass(params.wordmark, params.className);
      }
      throw new Error('Invalid parameters');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trademarks'] });
    },
  });

  return {
    trademarks,
    isLoading,
    error,
    refetch,
    ingest: ingestMutation.mutate,
    isIngesting: ingestMutation.isPending,
    ingestError: ingestMutation.error,
    ingestResult: ingestMutation.data,
  };
};
