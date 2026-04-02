package collector

import (
	"context"
	"fmt"
	"strings"
	"time"

	"github.com/google/uuid"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
)

func SendTestSpan(ctx context.Context, endpoint, token string) (string, error) {
	testSpanID := uuid.NewString()
	opts := []otlptracegrpc.Option{
		otlptracegrpc.WithEndpoint(strings.TrimPrefix(strings.TrimPrefix(endpoint, "http://"), "https://")),
	}
	if strings.HasPrefix(endpoint, "http://") {
		opts = append(opts, otlptracegrpc.WithInsecure())
	}
	if token != "" {
		opts = append(opts, otlptracegrpc.WithHeaders(map[string]string{"Authorization": "Bearer " + token}))
	}
	exporter, err := otlptracegrpc.New(ctx, opts...)
	if err != nil {
		return "", err
	}
	provider := sdktrace.NewTracerProvider(sdktrace.WithBatcher(exporter))
	defer func() {
		_ = provider.Shutdown(ctx)
	}()
	otel.SetTracerProvider(provider)
	tracer := provider.Tracer("agentsec-cli")
	_, span := tracer.Start(ctx, "agentsec.verify")
	span.SetAttributes(
		attribute.String("agentsec.span_type", "verify"),
		attribute.String("agentsec.token.present", fmt.Sprintf("%t", token != "")),
		attribute.String("agentsec.verify.timestamp", time.Now().Format(time.RFC3339)),
		attribute.String("agentsec.verify.span_id", testSpanID),
	)
	span.End()
	return testSpanID, provider.ForceFlush(ctx)
}
